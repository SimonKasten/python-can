"""
Enable basic CAN over a NI XNet device.
"""

from __future__ import absolute_import, print_function, division

from can import CanError, Message, BusABC
from can.bus import BusState

from can.interfaces.nixnet.errors import XnetError  # NOQA: F401
from can.interfaces.nixnet.errors import XnetResourceWarning  # NOQA: F401
from can.interfaces.nixnet.errors import XnetWarning  # NOQA: F401

from can.interfaces.nixnet import _enums as constants
from can.interfaces.nixnet import types


import typing  # NOQA: F401

from can.interfaces.nixnet import _frames
from can.interfaces.nixnet import _funcs
from can.interfaces.nixnet import _utils
from can.interfaces.nixnet._enums import CanCommState

from can.interfaces.nixnet._session import base


class NiXnetBus(BusABC):
    def __init__(
        self, channel="CAN3", state=BusState.ACTIVE, bitrate=None, *args, **kwargs
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

        super(NiXnetBus, self).__init__(
            channel=channel, state=state, bitrate=bitrate, *args, **kwargs
        )

    @property
    def state(self):
        """
        Query the NIXNET status of a session.

        :type: can.BusState
        """
        ###POMMES
        if (
            self.input_session.can_comm == CanCommState.BUS_OFF
            or self.output_session.can_comm == CanCommState.BUS_OFF
        ):
            return BusState.ERROR

        elif (
            self.input_session.can_comm == CanCommState.ERROR_PASSIVE
            or self.output_session.can_comm == CanCommState.ERROR_PASSIVE
        ):
            return BusState.PASSIVE

        elif (
            self.input_session.can_comm == CanCommState.ERROR_ACTIVE
            or self.output_session.can_comm == CanCommState.ERROR_ACTIVE
        ):
            return BusState.ACTIVE

    def flush_tx_buffer(self):
        """
        Flush NiXnet TX buffer
        """
        return self.output_session.flush()

    def _recv_internal(self, timeout):
        """
        Read a msg from NIXnet BUS
        """

        print("TODO: use python-can´s Message Class ")
        print("TODO: num_pend inc msg: ", self.input_session.num_pend)

        try:
            if timeout is None:
                timeout = constants.Timeouts.TIMEOUT_INFINITE
            buffer, num = _funcs.nx_read_frame(
                self.input_session._handle, _frames.nxFrameFixed_t.size, timeout
            )
            frame = _frames.parse_single_frame(buffer[:num])
            frame.channel = self.channel_info

        except:
            print("_recv_internal timed out")
            return None, True

        if frame:
            return frame, True

        return None, True

    def send(self, msg, timeout=None):
        if timeout is None:
            timeout = 0

        # frame = types.CanFrame(
        #     msg.arbitration_id, constants.FrameType.CAN_DATA, msg.data
        # )
        # byte_frame = b"".join(_frames.serialize_frame(frame.to_raw()))
        byte_frame = b"".join(_frames.serialize_can_msg(msg))
        
        _funcs.nx_write_frame(self.output_session._handle, byte_frame, timeout)
        print("Sent frame", msg)

    def __del__(self):
        print("Closing NIXNET Sessions")
        try:
            self.output_session.close()
            self.input_session.close()
        except:
            print("No Sessions created")


class NiXnetError(CanError):
    """
    A generic error on a NiXnetBus.
    """

    pass
