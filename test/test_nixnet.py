from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import unittest
from unittest import mock
import pytest

import can

from can.interfaces.nixnet import _frames
from can.interfaces.nixnet import errors


def raise_code(code):
    raise errors.XnetError("", code)


class TestNIXnetBus(unittest.TestCase):
    def setUp(self) -> None:
        # # basic mock for XLDriver
        # can.interfaces.vector.canlib.xldriver = Mock()

        # # bus creation functions
        # can.interfaces.vector.canlib.xldriver.xlOpenDriver = Mock()
        # can.interfaces.vector.canlib.xldriver.xlGetApplConfig = Mock(
        #     side_effect=xlGetApplConfig
        # )
        # can.interfaces.vector.canlib.xldriver.xlGetChannelIndex = Mock(
        #     side_effect=xlGetChannelIndex
        # )
        # can.interfaces.vector.canlib.xldriver.xlOpenPort = Mock(side_effect=xlOpenPort)
        # can.interfaces.vector.canlib.xldriver.xlCanFdSetConfiguration = Mock(
        #     return_value=0
        # )
        # can.interfaces.vector.canlib.xldriver.xlCanSetChannelMode = Mock(return_value=0)
        # can.interfaces.vector.canlib.xldriver.xlActivateChannel = Mock(return_value=0)
        # can.interfaces.vector.canlib.xldriver.xlGetSyncTime = Mock(
        #     side_effect=xlGetSyncTime
        # )
        # can.interfaces.vector.canlib.xldriver.xlCanSetChannelAcceptance = Mock(
        #     return_value=0
        # )
        # can.interfaces.vector.canlib.xldriver.xlCanSetChannelBitrate = Mock(
        #     return_value=0
        # )
        # can.interfaces.vector.canlib.xldriver.xlSetNotification = Mock(
        #     side_effect=xlSetNotification
        # )

        # # bus deactivation functions
        # can.interfaces.vector.canlib.xldriver.xlDeactivateChannel = Mock(return_value=0)
        # can.interfaces.vector.canlib.xldriver.xlClosePort = Mock(return_value=0)
        # can.interfaces.vector.canlib.xldriver.xlCloseDriver = Mock()

        # # sender functions
        # can.interfaces.vector.canlib.xldriver.xlCanTransmit = Mock(return_value=0)
        # can.interfaces.vector.canlib.xldriver.xlCanTransmitEx = Mock(return_value=0)

        # # various functions
        # can.interfaces.vector.canlib.xldriver.xlCanFlushTransmitQueue = Mock()
        # can.interfaces.vector.canlib.WaitForSingleObject = Mock()

        self.bus = None

    def tearDown(self) -> None:
        if self.bus:
            self.bus.shutdown()
            self.bus = None



    def test_parse_single_frame_with_empty_payload(self) -> None:
        payload = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        empty_bytes = b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x04\x05\x00' + payload
        empty_frame = _frames.parse_single_frame(empty_bytes)

        assert empty_frame.timestamp == 0x1
        assert empty_frame.arbitration_id == 0x2
        assert not empty_frame.is_extended_id
        assert empty_frame.dlc == 0
        assert empty_frame.data == b''
        assert not empty_frame.is_remote_frame
        assert not empty_frame.is_error_frame


    def test_parse_single_frame_with_base_payload(self) -> None:
        payload = b'\x01\x02\x03\x04\x05\x06\x07\x08'
        base_bytes = b'\x06\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00\x08\x09\x08' + payload
        base_frame = _frames.parse_single_frame(base_bytes)

        assert base_frame.timestamp == 0x6
        assert base_frame.arbitration_id == 0x7
        assert not base_frame.is_extended_id
        assert base_frame.dlc == 8
        assert base_frame.data == b'\x01\x02\x03\x04\x05\x06\x07\x08'
        assert not base_frame.is_remote_frame
        assert not base_frame.is_error_frame

    def test_parse_single_frame_with_partial_base_payload(self) -> None:
        frame_bytes = b'\xd8\xb7@B\xeb\xff\xd2\x01\x00\x00\x00\x00\x00\x00\x00\x04\x02\x04\x08\x10\x00\x00\x00\x00'
        frame = _frames.parse_single_frame(frame_bytes)

        assert frame.timestamp == 0x1d2ffeb4240b7d8
        assert frame.arbitration_id == 0x0
        assert not frame.is_extended_id
        assert frame.dlc == 4
        assert frame.data == b'\x02\x04\x08\x10'
        assert not frame.is_remote_frame
        assert not frame.is_error_frame


    @unittest.mock.patch('can.interfaces.nixnet._errors.check_for_error', raise_code)
    def test_parse_single_frame_corrupted_frame(self) -> None:
        empty_bytes = b'\x01\x00\x00\x00\x00\x00\x00'
        with pytest.raises(errors.XnetError):
            _frames.parse_single_frame(empty_bytes)




    def test_serialize_frame_with_empty_payload(self) -> None:
        emptry_can_msg = can.Message(arbitration_id=2, 
                                    is_extended_id=False,
                                    is_remote_frame=False,
                                    is_error_frame=False,
                                    data=b'')
        base = _frames.serialize_can_msg(emptry_can_msg)
        assert base[0:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00'
        assert base[16:] == b'\x00\x00\x00\x00\x00\x00\x00\x00'


    def test_serialize_frame_with_base_payload(self) -> None:
        payload = b'\x01\x02\x03\x04\x05\x06\x07\x08'
        base_can_msg = can.Message(arbitration_id=2,
                                    is_extended_id=False,
                                    is_remote_frame=False,
                                    is_error_frame=False,
                                    data=payload)
        base = _frames.serialize_can_msg(base_can_msg)
        assert base[0:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x08'
        assert base[16:] == b'\x01\x02\x03\x04\x05\x06\x07\x08'

    def test_serialize_extended_frame_with_base_payload(self) -> None:
        payload = b'\x03\xFF\xE3\x23\x03\xFE\xD1\x3E'
        base_can_msg = can.Message(arbitration_id=0x13EF3A2E,
                                    is_extended_id=True,
                                    is_remote_frame=False,
                                    is_error_frame=False,
                                    data=payload)
        base = _frames.serialize_can_msg(base_can_msg)
        assert base[0:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00.:\xef3\x00\x00\x00\x08'
        assert base[16:] == b'\x03\xFF\xE3\x23\x03\xFE\xD1\x3E'
                            
        #assert base[0:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00.:\xef3\x00\x00\x00\x08'
        #assert base[0:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00.:\xef3\x01\x00\x00\x08' remote
        #assert base[0:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00.:\xef3\x02\x00\x00\x08' error

    def test_serialize_frame_with_payload_unit(self) -> None:
        payload = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B'
        base_can_msg = can.Message(arbitration_id=2,
                                    is_extended_id=False,
                                    is_remote_frame=False,
                                    is_error_frame=False,
                                    data=payload)
        base = _frames.serialize_can_msg(base_can_msg)
        assert base[0:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x0b'
        assert base[16:] == b'\x01\x02\x03\x04\x05\x06\x07\x08'


    @unittest.mock.patch('can.interfaces.nixnet._errors.check_for_error', raise_code)
    def test_serialize_frame_with_excessive_payload(self) -> None:
        payload = 0xFF * b'\x01\x02\x03\x04\x05\x06\x07\x08'
        base_can_msg = can.Message(arbitration_id=2,
                            is_extended_id=False,
                            is_remote_frame=False,
                            is_error_frame=False,
                            data=payload)
        with pytest.raises(errors.XnetError):
            _frames.serialize_can_msg(base_can_msg)


if __name__ == "__main__":
    unittest.main()
