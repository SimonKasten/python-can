﻿from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import typing  # NOQA: F401

import six

from can.interfaces.nixnet import _cconsts
from can.interfaces.nixnet import _errors
from can.interfaces.nixnet import _enums as constants
from can.interfaces.nixnet import _types


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
    # type:  (int) -> _types.CanComm
    """Parse a CAN Comm bitfield."""
    state = constants.CanCommState(bitfield & 0x0F)
    tcvr_err = ((bitfield >> 4) & 0x01) != 0
    sleep = ((bitfield >> 5) & 0x01) != 0
    last_err = constants.CanLastErr((bitfield >> 8) & 0x0F)
    tx_err_count = (bitfield >> 16) & 0x0FF
    rx_err_count = (bitfield >> 24) & 0x0FF
    return _types.CanComm(state, tcvr_err, sleep, last_err, tx_err_count, rx_err_count)
