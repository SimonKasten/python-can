from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import unittest
from unittest import mock
from unittest.mock import Mock
import pytest


import can
from can.interfaces.nixnet import _frames
from can.interfaces.nixnet import _errors
from can.interfaces.nixnet import errors

from can.interfaces.nixnet import _cconsts
from can.interfaces.nixnet import _cfuncs
from can.interfaces.nixnet import _utils
from can.interfaces.nixnet import _enums
from can.interfaces.nixnet import _lib


def raise_code(code):
    raise errors.XnetError("", code)


class TestNIXnetBus(unittest.TestCase):
    def setUp(self) -> None:
        
        can.interfaces.nixnet._funcs = Mock()
        can.interfaces.nixnet._frames = Mock()
        self.bus = None

    def tearDown(self) -> None:
        if self.bus:
            self.bus.shutdown()
            self.bus = None


    # test_errors
    MockXnetLibrary = mock.create_autospec(_cfuncs.XnetLibrary, spec_set=True, instance=True)

    @mock.patch('can.interfaces.nixnet._cfuncs.lib', MockXnetLibrary)
    def test_success(self) -> None:
        _errors.check_for_error(_cconsts.NX_SUCCESS)

    @mock.patch('can.interfaces.nixnet._cfuncs.lib', MockXnetLibrary)
    def test_known_error(self) -> None:
        with pytest.raises(errors.XnetError) as excinfo:
            _errors.check_for_error(_enums.Err.SELF_TEST_ERROR1.value)
        assert excinfo.value.error_code == _enums.Err.SELF_TEST_ERROR1.value
        assert excinfo.value.error_type == _enums.Err.SELF_TEST_ERROR1
        assert excinfo.value.args == ('', )

    @mock.patch('can.interfaces.nixnet._cfuncs.lib', MockXnetLibrary)
    def test_unknown_error(self) -> None:
        error_code = -201232  # Arbitrary number
        # Ensure it is an unknown error
        with pytest.raises(ValueError):
            _enums.Err(error_code)

        with pytest.raises(errors.XnetError) as excinfo:
            _errors.check_for_error(error_code)
        assert excinfo.value.error_code == error_code
        assert excinfo.value.error_type == _enums.Err.INTERNAL_ERROR
        assert excinfo.value.args == ('', )


    @mock.patch('can.interfaces.nixnet._cfuncs.lib', MockXnetLibrary)
    def test_known_warning(self) -> None:
        with pytest.warns(errors.XnetWarning) as record:
            _errors.check_for_error(_enums.Warn.DATABASE_IMPORT.value)
        assert len(record) == 1
        assert record[0].message.warning_code == _enums.Warn.DATABASE_IMPORT.value
        assert record[0].message.warning_type == _enums.Warn.DATABASE_IMPORT
        assert record[0].message.args == ('Warning 1073098885 occurred.\n\n', )


    @mock.patch('can.interfaces.nixnet._cfuncs.lib', MockXnetLibrary)
    def test_unknown_warning(self) -> None:
        warning_code = 201232  # Arbitrary number
        # Ensure it is an unknown error
        with pytest.raises(ValueError):
            _enums.Warn(warning_code)

        with pytest.warns(errors.XnetWarning) as record:
            _errors.check_for_error(warning_code)
        assert len(record) == 1
        assert record[0].message.warning_code == warning_code
        assert record[0].message.warning_type is None
        assert record[0].message.args == ('Warning 201232 occurred.\n\n', )

    @pytest.mark.integration
    def test_driver_call(self) -> None:
        with pytest.raises(errors.XnetError) as excinfo:
            _errors.check_for_error(_enums.Err.SELF_TEST_ERROR1.value)
        assert excinfo.value.error_code == _enums.Err.SELF_TEST_ERROR1.value
        assert excinfo.value.error_type == _enums.Err.SELF_TEST_ERROR1
        assert '(Hex 0xBFF63002)' in excinfo.value.args[0]

    # test_frames
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

    def test_serialize_extended_remote_frame_with_base_payload(self) -> None:
        payload = b'\x03\xFF\xE3\x23\x03\xFE\xD1\x3E'
        base_can_msg = can.Message(arbitration_id=0x13EF3A2E,
                                    is_extended_id=True,
                                    is_remote_frame=True,
                                    is_error_frame=False,
                                    data=payload)
        base = _frames.serialize_can_msg(base_can_msg)
        assert base[0:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00.:\xef3\x01\x00\x00\x00'
        assert base[16:] == b'\x00\x00\x00\x00\x00\x00\x00\x00'
                            
    def test_serialize_extended_error_frame_with_base_payload(self) -> None:
        payload = b'\x03\xFF\xE3\x23\x03\xFE\xD1\x29'
        base_can_msg = can.Message(arbitration_id=0x13EF3A2E,
                                    is_extended_id=True,
                                    is_remote_frame=False,
                                    is_error_frame=True,
                                    data=payload)
        base = _frames.serialize_can_msg(base_can_msg)
        assert base[0:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00.:\xef3\x02\x00\x00\x08'
        assert base[16:] == b'\x03\xFF\xE3\x23\x03\xFE\xD1\x29'

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


    """test_lib"""
    def test_unsupported_platform(self) -> None:
        """Hard to make this a good test, so at least verifying the error reporting.

        For now, we'll just verify the calls don't call catastrophically fail and
        someone can always run py.test with ``-s``_.
        """
        with pytest.raises(_lib.PlatformUnsupportedError) as excinfo:
            _lib._import_unsupported()


    def test_function_not_supported(self) -> None:
        """Hard to make this a good test, so at least verifying the error reporting.

        For now, we'll just verify the calls don't call catastrophically fail and
        someone can always run py.test with ``-s``_.
        """
        ctypes_mock = object()
        lib = _lib.XnetLibrary(ctypes_mock)
        with pytest.raises(_lib.XnetFunctionNotSupportedError) as excinfo:
            lib.strange_and_unusual_funcion



    def test_parse_can_comm_bitfield(self) -> None:
        """A part of Session.can_comm"""
        comm = _utils.parse_can_comm_bitfield(0)
        assert comm == _utils.CanComm(
            _enums.CanCommState.ERROR_ACTIVE,
            tcvr_err=False,
            sleep=False,
            last_err=_enums.CanLastErr.NONE,
            tx_err_count=0,
            rx_err_count=0)

        comm = _utils.parse_can_comm_bitfield(0xFFFFF6F3)
        assert comm == _utils.CanComm(
            _enums.CanCommState.INIT,
            tcvr_err=True,
            sleep=True,
            last_err=_enums.CanLastErr.CRC,
            tx_err_count=255,
            rx_err_count=255)









if __name__ == "__main__":
    unittest.main()
