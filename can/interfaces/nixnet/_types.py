from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# import abc
import collections
import typing  # NOQA: F401

# import six

from can.interfaces.nixnet import _cconsts
from can.interfaces.nixnet import _errors

# from . import _py2
# from . import _enums as constants

__all__ = [
    "CanComm",
    "CanIdentifier"
]

CanComm_ = collections.namedtuple(
    "CanComm_",
    ["state", "tcvr_err", "sleep", "last_err", "tx_err_count", "rx_err_count"],
)


class CanComm(CanComm_):
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



class CanIdentifier(object):
    """CAN frame arbitration identifier.

    Attributes:
        identifier(int): CAN frame arbitration identifier
        extended(bool): If the identifier is extended
    """

    _FRAME_ID_MASK = 0x000007FF
    _EXTENDED_FRAME_ID_MASK = 0x1FFFFFFF

    def __init__(self, identifier, extended=False):
        # type: (int, bool) -> None
        self.identifier = identifier
        self.extended = extended

    @classmethod
    def from_raw(cls, raw):
        # type: (int) -> CanIdentifier
        """Parse a raw frame identifier into a CanIdentifier

        Args:
            raw(int): A raw frame identifier

        Returns:
            CanIdentifier: parsed value

        >>> CanIdentifier.from_raw(0x1)
        CanIdentifier(0x1)
        >>> CanIdentifier.from_raw(0x20000001)
        CanIdentifier(0x1, extended=True)
        """
        extended = bool(raw & _cconsts.NX_FRAME_ID_CAN_IS_EXTENDED)
        if extended:
            identifier = raw & cls._EXTENDED_FRAME_ID_MASK
        else:
            identifier = raw & cls._FRAME_ID_MASK
        return cls(identifier, extended)

    def __int__(self):
        """Convert CanIdentifier into a raw frame identifier

        >>> hex(int(CanIdentifier(1)))
        '0x1'
        >>> hex(int(CanIdentifier(1, True)))
        '0x20000001'
        """
        identifier = self.identifier
        if self.extended:
            if identifier != (identifier & self._EXTENDED_FRAME_ID_MASK):
                _errors.check_for_error(_cconsts.NX_ERR_UNDEFINED_FRAME_ID)
            identifier |= _cconsts.NX_FRAME_ID_CAN_IS_EXTENDED
        else:
            if identifier != (identifier & self._FRAME_ID_MASK):
                _errors.check_for_error(_cconsts.NX_ERR_UNDEFINED_FRAME_ID)
        return identifier

    def __eq__(self, other):
        if isinstance(other, CanIdentifier):
            other_id = typing.cast(CanIdentifier, other)
            return all(
                (
                    self.identifier == other_id.identifier,
                    self.extended == other_id.extended,
                )
            )
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

    def __repr__(self):
        """CanIdentifier debug representation.

        >>> CanIdentifier(1)
        CanIdentifier(0x1)
        >>> CanIdentifier(1, True)
        CanIdentifier(0x1, extended=True)
        """
        if self.extended:
            return "{}(0x{:x}, extended={})".format(
                type(self).__name__, self.identifier, self.extended
            )
        else:
            return "{}(0x{:x})".format(type(self).__name__, self.identifier)
