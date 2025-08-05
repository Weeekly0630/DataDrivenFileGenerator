from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, List, Callable, Optional, Protocol, Tuple


class Signal(Enum):
    ENTRY = auto()
    EXIT = auto()
    CUSTOM = auto()


@dataclass
class EventType:
    signal: Signal
    data: Any = None


class EventDrivenFsmReturnType(Enum):
    UNHANDLED = auto()
    HANDLED = auto()


class StateType(Protocol):
    def __call__(self, event: EventType) -> EventDrivenFsmReturnType: ...


@dataclass
class EventDrivenFsm:
    """Hierarchical Event Driven FSM."""

    state: StateType
    event_queue: List[EventType] = field(default_factory=list)
    parent: Optional["EventDrivenFsm"] = None

    def __post_init__(self):
        # Automatically add ENTRY event for initial state
        self._add_event(EventType(signal=Signal.ENTRY))

    def _drive(self) -> None:
        """Process the event queue and drive the FSM and its children."""
        while self.event_queue:
            cur_event = self.event_queue.pop(0)
            result = self.state(cur_event)
            # Propagate to parent if unhandled
            if result == EventDrivenFsmReturnType.UNHANDLED and self.parent:
                self.parent._add_event(cur_event)

    def _add_child(self, child: "EventDrivenFsm") -> None:
        """Add a child FSM to the current FSM."""
        child.parent = self

    def _add_event(self, event: EventType) -> None:
        """Add an event to the event queue."""
        self.event_queue.append(event)

    def transition(self, new_state: StateType) -> None:
        """Transition to a new state, handling EXIT and ENTRY."""
        self.state(EventType(signal=Signal.EXIT))
        self.state = new_state
        self.state(EventType(signal=Signal.ENTRY))

    def dispath(self, event: EventType) -> None:
        """发布事件（对外接口）"""
        self._add_event(event)
        self._drive()



