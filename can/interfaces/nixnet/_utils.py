from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import typing  # NOQA: F401

import six

from can.interfaces.nixnet import _cconsts
from can.interfaces.nixnet import _errors
from can.interfaces.nixnet import _enums as constants


_CanComm = collections.namedtuple(
    "_CanComm",
    ["state", "tcvr_err", "sleep", "last_err", "tx_err_count", "rx_err_count"],
)


class CanComm(_CanComm):
    """CAN Communication State.

    Attributes:
        state (:any:`nixnet._enums.CanCommState`): Communication State
        tcvr_err (bool): Transceiver Error.
            Transceiver error indicates whether an error condition exists on
            the physical transceiver. This is typically referred to as the
            transceiver chip NERR pin.  False indicates normal operation (no
            error), and true indicates an error.
        sleep (bool): Sleep.
            Sleep indicates whether the transceiver and communication
            controller are in their sleep state. False indicates normal
            operation (awake), and true indicates sleep.
        last_err (:any:`nixnet._enums.CanLastErr`): Last Error.
            Last error specifies the status of the last attempt to receive or
            transmit a frame
        tx_err_count (int): Transmit Error Counter.
            The transmit error counter begins at 0 when communication starts on
            the CAN interface. The counter increments when an error is detected
            for a transmitted frame and decrements when a frame transmits
            successfully. The counter increases more for an error than it is
            decreased for success. This ensures that the counter generally
            increases when a certain ratio of frames (roughly 1/8) encounter
            errors.
            When communication state transitions to Bus Off, the transmit error
            counter no longer is valid.
        rx_err_count (int): Receive Error Counter.
            The receive error counter begins at 0 when communication starts on
            the CAN interface. The counter increments when an error is detected
            for a received frame and decrements when a frame is received
            successfully. The counter increases more for an error than it is
            decreased for success. This ensures that the counter generally
            increases when a certain ratio of frames (roughly 1/8) encounter
            errors.
    """

    pass



def flatten_items(_list):
    # type: (typing.Union[typing.Text, typing.List[typing.Text]]) -> typing.Text
    """Flatten an item list to a string

    >>> str(flatten_items('Item'))
    'Item'
    >>> str(flatten_items(['A', 'B']))
    'A,B'
    >>> str(flatten_items(None))
    ''
    """
    if isinstance(_list, six.string_types):
        # For FRAME_IN_QUEUED / FRAME_OUT_QUEUED
        # Convenience for everything else
        if "," in _list:
            _errors.raise_xnet_error(_cconsts.NX_ERR_INVALID_PROPERTY_VALUE)
        flattened = _list
    elif isinstance(_list, collections.Iterable):
        flattened = ",".join(_list)
    elif _list is None:
        # For FRAME_IN_STREAM / FRAME_OUT_STREAM
        flattened = ""
    else:
        _errors.raise_xnet_error(_cconsts.NX_ERR_INVALID_PROPERTY_VALUE)

    return flattened


def parse_can_comm_bitfield(bitfield):
    # type:  (int) -> CanComm
    """Parse a CAN Comm bitfield."""
    state = constants.CanCommState(bitfield & 0x0F)
    tcvr_err = ((bitfield >> 4) & 0x01) != 0
    sleep = ((bitfield >> 5) & 0x01) != 0
    last_err = constants.CanLastErr((bitfield >> 8) & 0x0F)
    tx_err_count = (bitfield >> 16) & 0x0FF
    rx_err_count = (bitfield >> 24) & 0x0FF
    return CanComm(state, tcvr_err, sleep, last_err, tx_err_count, rx_err_count)
