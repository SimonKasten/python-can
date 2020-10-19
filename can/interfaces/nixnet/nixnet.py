"""
Enable basic CAN over a NI XNet device.
"""

from __future__ import absolute_import, print_function, division

import time

from can import BusABC
from can.bus import BusState
from can.interfaces.nixnet.errors import XnetError, XnetResourceWarning, XnetWarning  # NOQA


from can.interfaces.nixnet import _enums as constants
from can.interfaces.nixnet import _frames
from can.interfaces.nixnet import _funcs
from can.interfaces.nixnet import _utils
from can.interfaces.nixnet._enums import CanCommState

from can.interfaces.nixnet._session import base


class NiXnetBus(BusABC):
    """A NI XNet Bus."""

    def __init__(
        self, channel="CAN1", state=BusState.ACTIVE, bitrate=None, *args, **kwargs
    ):
        """A NI XNet interface to CAN."""

        self.channel_info = channel

        flattened_list = _utils.flatten_items(None)
        self.input_session = base.SessionBase(
            ":memory:",  # database_name,
            "",  # cluster_name,
            flattened_list,
            self.channel_info,
            constants.CreateSessionMode.FRAME_IN_STREAM,
        )

        flattened_list = _utils.flatten_items(None)
        self.output_session = base.SessionBase(
            ":memory:",  # database_name,
            "",  # cluster_name,
            flattened_list,
            self.channel_info,
            constants.CreateSessionMode.FRAME_OUT_STREAM,
        )

        self.input_session.intf.can_term = constants.CanTerm.ON
        self.output_session.intf.can_term = constants.CanTerm.ON

        self.input_session.intf.baud_rate = bitrate
        self.output_session.intf.baud_rate = bitrate

        self.input_session.start()
        self.output_session.start()
        self.input_session.flush()
        self.output_session.flush()


        super(NiXnetBus, self).__init__(
            channel=channel, state=state, bitrate=bitrate, *args, **kwargs
        )

    @property
    def state(self):
        """
        Query the NIXNET status of a session.

        :type: can.BusState
        """
        if (
            self.input_session.can_comm.state == CanCommState.BUS_OFF
            or self.output_session.can_comm.state == CanCommState.BUS_OFF
        ):
            return BusState.ERROR

        if (
            self.input_session.can_comm.state == CanCommState.ERROR_PASSIVE
            or self.output_session.can_comm.state == CanCommState.ERROR_PASSIVE
        ):
            return BusState.PASSIVE

        if (
            self.input_session.can_comm.state == CanCommState.ERROR_ACTIVE
            or self.output_session.can_comm.state == CanCommState.ERROR_ACTIVE
        ):
            return BusState.ACTIVE

    def flush_tx_buffer(self):
        """
        Flush NiXnet TX buffer
        """
        return self.output_session.flush()

    def _recv_internal(self, timeout=constants.Timeouts.TIMEOUT_NONE):
        """
        Read a msg from NIXnet BUS
        """
        if timeout is None:
            timeout = 0

        if self.input_session.num_pend:
            buffer, num = _funcs.nx_read_frame(
                self.input_session.handle, _frames.nxFrameFixed_t.size, timeout
            )

            frame = _frames.parse_single_frame(buffer[:num])
            frame.channel = self.channel_info

            if frame:
                return frame, True
        # no pending Message
        return None, True


    def send(self, msg, timeout=constants.Timeouts.TIMEOUT_NONE):
        if timeout is None:
            timeout = 0

        if self.output_session.num_pend < 100:
            byte_frame = b"".join(_frames.serialize_can_msg(msg))
            _funcs.nx_write_frame(self.output_session.handle, byte_frame, timeout)


    def __del__(self):
        print("Closing NIXNET Sessions")
        try:
            self.output_session.close()
            self.input_session.close()
        except:
            print("No Sessions created")
