﻿from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import typing  # NOQA: F401

import six

from can.interfaces.nixnet import _props
from can.interfaces.nixnet import _enums as constants


class Interface(object):
    """Interface configuration for a session"""

    def __init__(self, handle):
        # type: (int) -> None
        self._handle = handle

    def __repr__(self):
        return "{}(handle={})".format(type(self).__name__, self._handle)

    def __str__(self):
        return self._name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._name == other._name
        elif isinstance(other, six.string_types):
            return self._name == other
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

    @property
    def baud_rate(self):
        # type: () -> int
        """int: CAN interface baud rate.

        The default value for this interface property is the same as the
        cluster's baud rate in the database. Your application can set this
        interface baud rate to override the value in the database, or when no
        database is used.

        **CAN**

        When the upper nibble (0xF0000000) is clear, this is a numeric baud
        rate (for example, 500000).

        NI-XNET CAN hardware currently accepts the following numeric baud
        rates: 33333, 40000, 50000, 62500, 80000, 83333, 100000, 125000,
        160000, 200000, 250000, 400000, 500000, 800000, and 1000000.

        **LIN**

        When the upper nibble (0xF0000000) is clear, you can set only baud
        rates within the LIN-specified range (2400 to 20000) for the interface.
        """
        return _props.get_session_intf_baud_rate64(self._handle)

    @baud_rate.setter
    def baud_rate(self, value):
        # type: (int) -> None
        _props.set_session_intf_baud_rate64(self._handle, value)

    @property
    def bus_err_to_in_strm(self):
        # type: () -> bool
        """bool: Bus Error Frames to Input Stream?

        Specifies whether the hardware should place a CAN or LIN bus error
        frame into the Stream Input queue after it is generated.
        """
        return _props.get_session_intf_bus_err_to_in_strm(self._handle)

    @bus_err_to_in_strm.setter
    def bus_err_to_in_strm(self, value):
        # type: (bool) -> None
        _props.set_session_intf_bus_err_to_in_strm(self._handle, value)

    @property
    def echo_tx(self):
        # type: () -> bool
        """bool: Echo Transmit?

        Determines whether Frame Input or Signal Input sessions contain frames
        that the interface transmits.

        When this property is true, and a frame transmit is complete for an
        Output session, the frame is echoed to the Input session. Frame Input
        sessions can use the Flags field to differentiate frames received from
        the bus and frames the interface transmits. When reading frames with
        the :any:`nixnet.types.RawFrame`, you can parse the Flags field
        manually by reviewing the Raw Frame Format section. Signal Input
        sessions cannot differentiate the origin of the incoming data.

        .. note:: Echoed frames are placed into the input sessions only after
           the frame transmit is complete. If there are bus problems (for
           example, no listener) such that the frame did not transmit, the
           frame is not received.
        """
        return _props.get_session_intf_echo_tx(self._handle)

    @echo_tx.setter
    def echo_tx(self, value):
        # type: (bool) -> None
        _props.set_session_intf_echo_tx(self._handle, value)

    @property
    def out_strm_list_by_id(self):
        # type: () -> typing.Iterable[int]
        """int: Output Stream List by Frame Identifier.

        Provide a list of frames for use with the replay feature
        Interface:Output Stream Timing property.

        This property serves the same purpose as Interface:Output Stream List,
        in that it provides a list of frames for replay filtering. This
        property provides an alternate format for you to specify the frames by
        their CAN arbitration ID or LIN unprotected ID. The property's data
        type is an array of integers. Each integer represents a CAN or LIN
        frame's identifier, using the same encoding as :any:`nixnet.types.RawFrame`.

        LIN frame ID values may be within the range of possible LIN
        IDs (0-63).

        See also :any:`Interface.out_strm_list`.
        """
        for _id in _props.get_session_intf_can_out_strm_list_by_id(self._handle):
            yield _id

    @out_strm_list_by_id.setter
    def out_strm_list_by_id(self, value):
        # type: (typing.Iterable[int]) -> None
        _props.set_session_intf_can_out_strm_list_by_id(self._handle, list(value))

    @property
    def out_strm_timng(self):
        # type: () -> constants.OutStrmTimng
        """:any:`nixnet._enums.OutStrmTimng`: Output Stream Timing.

        The Output Stream Timing property configures how the hardware transmits
        frames queued using a Frame Output Stream session.

        See also :any:`Interface.out_strm_list`.

        .. note:: Only CAN and LIN interfaces currently support this property.
        """
        return constants.OutStrmTimng(
            _props.get_session_intf_out_strm_timng(self._handle)
        )

    @out_strm_timng.setter
    def out_strm_timng(self, value):
        # type: (constants.OutStrmTimng) -> None
        _props.set_session_intf_out_strm_timng(self._handle, value.value)

    @property
    def start_trig_to_in_strm(self):
        # type: () -> bool
        """bool: Start Trigger Frames to Input Stream?

        Configures the hardware to place a start trigger frame into the Stream
        Input queue after it is generated. A Start Trigger frame is generated
        when the interface is started.

        The start trigger frame is especially useful if you plan to log and
        replay CAN data.
        """
        return _props.get_session_intf_start_trig_to_in_strm(self._handle)

    @start_trig_to_in_strm.setter
    def start_trig_to_in_strm(self, value):
        # type: (bool) -> None
        _props.set_session_intf_start_trig_to_in_strm(self._handle, value)

    def set_can_ext_tcvr_config(self, value):
        # type: (int) -> None
        """Configure XS series CAN hardware to communicate properly with your external transceiver.

        Args:
            value(int): Bitfield
        """
        _props.set_session_intf_can_ext_tcvr_config(self._handle, value)

    @property
    def can_lstn_only(self):
        # type: () -> bool
        """bool:  Listen Only? property configures whether the CAN interface transmits any
        information to the CAN bus.

        When this property is false, the interface can transmit CAN frames and
        acknowledge received CAN frames.

        When this property is true, the interface can neither transmit CAN
        frames nor acknowledge a received CAN frame. The true value enables
        passive monitoring of network traffic, which can be useful for
        debugging scenarios when you do not want to interfere with a
        communicating network cluster.
        """
        return _props.get_session_intf_can_lstn_only(self._handle)

    @can_lstn_only.setter
    def can_lstn_only(self, value):
        # type: (bool) -> None
        _props.set_session_intf_can_lstn_only(self._handle, value)

    @property
    def can_pend_tx_order(self):
        # type: () -> constants.CanPendTxOrder
        """:any:`nixnet._enums.CanPendTxOrder`: Pending Transmit Order

        The Pending Transmit Order property configures how the CAN interface
        manages the internal queue of frames. More than one frame may desire to
        transmit at the same time. NI-XNET stores the frames in an internal
        queue and transmits them onto the CAN bus when the bus is idle.

        .. note:: You can modify this property only when the interface is
           stopped.
        .. note:: Setting this property causes the internal queue to be flushed.
           If you start a session, queue frames, and then stop the session and
           change this mode, some frames may be lost. Set this property to the
           desired value once; do not constantly change modes.
        """
        return constants.CanPendTxOrder(
            _props.get_session_intf_can_pend_tx_order(self._handle)
        )

    @can_pend_tx_order.setter
    def can_pend_tx_order(self, value):
        # type: (constants.CanPendTxOrder) -> None
        _props.set_session_intf_can_pend_tx_order(self._handle, value.value)

    @property
    def can_sing_shot(self):
        # type: () -> bool
        """bool: Single Shot Transmit?

        The Single Shot Transmit? property configures whether the CAN interface
        retries failed transmissions.

        When this property is false, failed transmissions retry as specified by
        the CAN protocol (ISO 11898-1, 6.11 Automatic Retransmission). If a CAN
        frame is not transmitted successfully, the interface attempts to
        retransmit the frame as soon as the bus is idle again. This retransmit
        process continues until the frame is successfully transmitted.

        When this property is true, failed transmissions do not retry. If a CAN
        frame is not transmitted successfully, no further transmissions are
        attempted.

        .. note:: You can modify this property only when the interface is
           stopped.
        .. note:: Setting this property causes the internal queue to be flushed.
           If you start a session, queue frames, and then stop the session and
           change this mode, some frames may be lost. Set this property to the
           desired value once; do not constantly change modes.
        """
        return _props.get_session_intf_can_sing_shot(self._handle)

    @can_sing_shot.setter
    def can_sing_shot(self, value):
        # type: (bool) -> None
        _props.set_session_intf_can_sing_shot(self._handle, value)

    @property
    def can_term(self):
        # type: () -> constants.CanTerm
        """:any:`nixnet._enums.CanTerm`: CAN Termination.

        The Termination property configures the onboard termination of the
        NI-XNET interface CAN connector (port). The enumeration is generic and
        supports two values: Off and On. However, different CAN hardware has
        different termination requirements, and the Off and On values have
        different meanings, see :any:`nixnet._enums.CanTerm`.

        .. note:: You can modify this property only when the interface is
           stopped.
        .. note:: This property does not take effect until the interface is
           started.
        """
        return constants.CanTerm(_props.get_session_intf_can_term(self._handle))

    @can_term.setter
    def can_term(self, value):
        # type: (constants.CanTerm) -> None
        _props.set_session_intf_can_term(self._handle, value.value)

    @property
    def can_tcvr_state(self):
        # type: () -> constants.CanTcvrState
        """:any:`nixnet._enums.CanTcvrState`: CAN Transceiver State.

        The Transceiver State property configures the CAN transceiver and CAN
        controller modes. The transceiver state controls whether the
        transceiver is asleep or communicating, as well as configuring other
        special modes.
        """
        return constants.CanTcvrState(
            _props.get_session_intf_can_tcvr_state(self._handle)
        )

    @can_tcvr_state.setter
    def can_tcvr_state(self, value):
        # type: (constants.CanTcvrState) -> None
        _props.set_session_intf_can_tcvr_state(self._handle, value.value)

    @property
    def can_tcvr_type(self):
        # type: () -> constants.CanTcvrType
        """:any:`nixnet._enums.CanTcvrType`: CAN Transceiver Type.

        For XNET hardware that provides a software-selectable transceiver, the
        Transceiver Type property allows you to set the transceiver type. Use
        the XNET Interface CAN.Tranceiver Capability property to determine
        whether your hardware supports a software-selectable transceiver.

        The default value for this property depends on your type of hardware.
        If you have fixed-personality hardware, the default value is the
        hardware value. If you have hardware that supports software-selectable
        transceivers, the default is High-Speed.
        """
        return constants.CanTcvrType(
            _props.get_session_intf_can_tcvr_type(self._handle)
        )

    @can_tcvr_type.setter
    def can_tcvr_type(self, value):
        # type: (constants.CanTcvrType) -> None
        _props.set_session_intf_can_tcvr_type(self._handle, value.value)

    @property
    def can_io_mode(self):
        # type: () -> constants.CanIoMode
        """:any:`nixnet._enums.CanIoMode`: CAN IO Mode.

        This property indicates the I/O Mode the interface is using.

        The value is initialized from the database cluster when the session is
        created and cannot be changed later. However, you can transmit standard
        CAN frames on a CAN FD network.
        """
        return constants.CanIoMode(_props.get_session_intf_can_io_mode(self._handle))

    @property
    def can_fd_baud_rate(self):
        # type: () -> int
        """int: The fast data baud rate for :any:`can_io_mode` of
        :any:`nixnet._enums.CanIoMode` ``CAN_FD_BRS``

        The default value for this interface property is the same as the
        cluster's FD baud rate in the database. Your application can set this
        interface FD baud rate to override the value in the database.

        When the upper nibble (0xF0000000) is clear, this is a numeric baud
        rate (for example, 500000).

        NI-XNET CAN hardware currently accepts the following numeric baud
        rates: 200000, 250000, 400000, 500000, 800000, 1000000, 1250000,
        1600000, 2000000, 2500000, 4000000, 5000000, and 8000000.

        .. note:: Not all CAN transceivers are rated to transmit at the requested
           rate. If you attempt to use a rate that exceeds the transceiver's
           qualified rate, XNET Start returns a warning. NI-XNET Hardware
           Overview describes the CAN transceivers' limitations.
        """
        return _props.get_session_intf_can_fd_baud_rate64(self._handle)

    @can_fd_baud_rate.setter
    def can_fd_baud_rate(self, value):
        # type: (int) -> None
        _props.set_session_intf_can_fd_baud_rate64(self._handle, value)

    @property
    def can_tx_io_mode(self):
        # type: () -> constants.CanIoMode
        """:any:`nixnet._enums.CanIoMode`: CAN Transmit IO Mode

        This property specifies the I/O Mode the interface uses when
        transmitting a CAN frame. By default, it is the same as the XNET
        Cluster CAN:I/O Mode property. However, even if the interface is in CAN
        FD+BRS mode, you can force it to transmit frames in the standard CAN
        format. For this purpose, set this property to CAN.

        The Transmit I/O mode may not exceed the mode set by the XNET Cluster
        CAN:I/O Mode property.

        .. note:: This property is not supported in CAN FD+BRS ISO mode. If you
           are using ISO CAN FD mode, you define the transmit I/O mode in the
           database with the I/O Mode property of the frame. (When a database
           is not used (for example, in frame stream mode), define the transmit
           I/O mode with the frame type field of the frame data.) Note that ISO
           CAN FD mode is the default mode for CAN FD in NI-XNET.
        .. note:: This property affects only the transmission of frames. Even if
           you set the transmit I/O mode to CAN, the interface still can
           receive frames in FD modes (if the XNET Cluster CAN:I/O Mode
           property is configured in an FD mode).
        """
        return constants.CanIoMode(_props.get_session_intf_can_tx_io_mode(self._handle))

    @can_tx_io_mode.setter
    def can_tx_io_mode(self, value):
        # type: (constants.CanIoMode) -> None
        _props.set_session_intf_can_tx_io_mode(self._handle, value.value)

    @property
    def can_fd_iso_mode(self):
        # type: () -> constants.CanFdIsoMode
        """:any:`nixnet._enums.CanFdIsoMode`: CAN FS ISO Mode.

        This property is valid only when the interface is in CAN FD(+BRS) mode.
        It specifies whether the interface is working in the ISO CAN FD
        standard (ISO standard 11898-1:2015) or non-ISO CAN FD standard (Bosch
        CAN FD 1.0 specification). Two ports using different standards (ISO CAN
        FD vs. non-ISO CAN FD) cannot communicate with each other.

        When you use a CAN FD database (DBC or FIBEX file created with
        NI-XNET), you can specify the ISO CAN FD mode when creating an alias
        name for the database. An alias is created automatically when you open
        a new database in the NI-XNET Database Editor. The specified ISO CAN FD
        mode is used as default, which you can change in the session using this
        property.
        """
        return constants.CanFdIsoMode(
            _props.get_session_intf_can_fd_iso_mode(self._handle)
        )

    @can_fd_iso_mode.setter
    def can_fd_iso_mode(self, value):
        # type: (constants.CanFdIsoMode) -> None
        _props.set_session_intf_can_fd_iso_mode(self._handle, value.value)

    @property
    def can_edge_filter(self):
        # type: () -> bool
        """bool: CAN Enable Edge Filter.

        When this property is enabled, the CAN hardware requires two
        consecutive dominant tq for hard synchronization.
        """
        return _props.get_session_intf_can_edge_filter(self._handle)

    @can_edge_filter.setter
    def can_edge_filter(self, value):
        # type: (bool) -> None
        _props.set_session_intf_can_edge_filter(self._handle, value)

    @property
    def can_transmit_pause(self):
        # type: () -> bool
        """bool: CAN Transmit Pause.

        When this property is enabled, the CAN hardware waits for two bit times
        before transmitting the next frame. This allows other CAN nodes to
        transmit lower priority CAN messages while this CAN node is
        transmitting high-priority CAN messages with high speed.
        """
        return _props.get_session_intf_can_transmit_pause(self._handle)

    @can_transmit_pause.setter
    def can_transmit_pause(self, value):
        # type: (bool) -> None
        _props.set_session_intf_can_transmit_pause(self._handle, value)

    @property
    def can_disable_prot_exception_handling(self):
        # type: () -> bool
        """bool: CAN Disable Protocol Exception Handling.

        A protocol exception occurs when the CAN hardware detects an invalid
        combination of bits on the CAN bus reserved for a future protocol
        expansion. NI-XNET allows you to define how the hardware should behave
        in case of a protocol exception:

        False (default): the CAN hardware stops receiving frames and starts a bus integration.

        True: the CAN hardware transmits an error frame when it detects a
        protocol exception condition.
        """
        return _props.get_session_intf_can_disable_prot_exception_handling(self._handle)

    @can_disable_prot_exception_handling.setter
    def can_disable_prot_exception_handling(self, value):
        # type: (bool) -> None
        _props.set_session_intf_can_disable_prot_exception_handling(self._handle, value)

    @property
    def src_term_start_trigger(self):
        # type: () -> typing.Text
        """string: Source Terminal Start Trigger

        Specifies the name of the internal terminal to use as the interface
        Start Trigger.

        This property is supported for C Series modules in a CompactDAQ
        chassis. It is not supported for CompactRIO, PXI, or PCI (refer to
        :any:`nixnet._session.base.SessionBase.connect_terminals` for those platforms).

        The digital trigger signal at this terminal is for the Start Interface
        transition, to begin communication for all sessions that use the
        interface. This property routes the start trigger, but not the timebase
        (used for timestamp of received frames and cyclic transmit of frames).
        Routing the timebase is not required for CompactDAQ, because all
        modules in the chassis automatically use a shared timebase.

        Use this property to connect the interface Start Trigger to triggers in
        other modules and/or interfaces. When you read this property, you
        specify the interface Start Trigger as the source of a connection. When
        you write this property, you specify the interface Start Trigger as the
        destination of a connection, and the value you write represents the
        source.

        The connection this property creates is disconnected when you clear
        (close) all sessions that use the interface.
        """
        return _props.get_session_intf_src_term_start_trigger(self._handle)

    @src_term_start_trigger.setter
    def src_term_start_trigger(self, value):
        # type: (typing.Text) -> None
        _props.set_session_intf_src_term_start_trigger(self._handle, value)

    @property
    def _name(self):
        # type: () -> typing.Text
        return _props.get_session_intf_name(self._handle)
