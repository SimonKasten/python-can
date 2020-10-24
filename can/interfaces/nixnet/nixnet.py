"""
Enable basic CAN over a NI XNet device.
"""

# TODO implement CAN FD
# TODO check frames serialze method

from __future__ import absolute_import, print_function, division

from can import BusABC
from can.bus import BusState

from can.interfaces.nixnet import _enums as constants
from can.interfaces.nixnet import _frames
from can.interfaces.nixnet import _funcs
from can.interfaces.nixnet import _utils
from can.interfaces.nixnet._enums import CanCommState

from can.interfaces.nixnet._cconsts import NX_PROP_SYS_DEV_REFS
import can.interfaces.nixnet.system as system


from can.interfaces.nixnet._session import base


class NiXnetBus(BusABC):
    """A NI XNet Bus."""

    @staticmethod
    def _detect_available_configs():
        """List connected NI XNet interfaces."""
        try:
            _handle = None
            _handle = _funcs.nx_system_open()
            _devices = system._collection.SystemCollection(
                _handle, NX_PROP_SYS_DEV_REFS, system._device.Device
            )

        except NameError:
            # no devices found, so no configurations are available
            return []

        channels = []
        row = {"interface": "nixnet", "device": "", "serialNr": "", "channel": []}

        for device in _devices:
            row["device"] = device.product_name
            row["serialNr"] = device.ser_num

            for intf in device.intf_refs_all:
                row["channel"].append(intf._name)
                channels.append(row)

        return channels

    def __init__(
        self, channel="CAN1", state=BusState.ACTIVE, bitrate=None, *args, **kwargs
    ):
        """A NI XNet interface to CAN."""

        self.channel_info = channel

        self.input_session = base.SessionBase(
            self.channel_info,
            constants.CreateSessionMode.FRAME_IN_STREAM,
        )

        self.output_session = base.SessionBase(
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

    @property
    def tx_num_pend(self):
        """
        Return number of pending TX Frames
        """
        return self.output_session.num_pend

    @property
    def rx_num_pend(self):
        """
        Return number of pending RX Frames
        """
        return self.input_session.num_pend

    def flush_tx_buffer(self):
        """
        Flush NiXnet TX buffer
        """
        return self.output_session.flush()

    def _recv_internal(self, timeout):
        """
        Read a msg from NIXnet BUS
        """
        if timeout is None:
            timeout = constants.Timeouts.TIMEOUT_NONE.value

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

    def send(self, msg, timeout=constants.Timeouts.TIMEOUT_INFINITE.value):
        if timeout is None:
            timeout = constants.Timeouts.TIMEOUT_INFINITE.value

        byte_frame = _frames.serialize_can_msg(msg)
        _funcs.nx_write_frame(self.output_session.handle, byte_frame, timeout)

    def __del__(self):
        print("Closing NIXNET Sessions")
        try:
            self.output_session.close()
            self.input_session.close()
        except:
            print("No Sessions created")
