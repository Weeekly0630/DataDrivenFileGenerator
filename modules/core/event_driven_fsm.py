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
        self.state(EventType(signal=Signal.ENTRY))

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

class FunctionFSM:
    """Active Object for function parsing."""

    class FunctionFSMSignal(Enum):
        """Signals for FunctionFSM custom actions (e.g., set function name, add argument)."""
        SET_FUNCTION_NAME = auto()
        ADD_ARGUMENT = auto()

    @dataclass
    class FunctionFSMState:
        """State data for FunctionFSM, storing function name and argument list."""
        function_name: str = ""
        args: List[Any] = field(default_factory=list)

    def __init__(self) -> None:
        self._parent = EventDrivenFsm(self._init_state)
        self._state = self.FunctionFSMState()

    @dataclass
    class FunctionFSMData:
        """Event data for FunctionFSM, carrying a FunctionFSMSignal and associated value."""
        signal: "FunctionFSM.FunctionFSMSignal"
        value: Any = None

    def _init_state(self, event: EventType) -> EventDrivenFsmReturnType:
        result: EventDrivenFsmReturnType

        # 处理自定义事件
        if event.signal == Signal.CUSTOM and isinstance(
            event.data, self.FunctionFSMData
        ):
            if event.data.signal == self.FunctionFSMSignal.SET_FUNCTION_NAME:
                self._state.function_name = event.data.value
            elif event.data.signal == self.FunctionFSMSignal.ADD_ARGUMENT:
                self._state.args.append(event.data.value)
            else:
                raise ValueError(f"Unknown FunctionFSMSignal: {event.data.signal}")
            result = EventDrivenFsmReturnType.HANDLED
        elif event.signal == Signal.EXIT:
            # 当前状态机结束，将结果返回上层状态机。
            parent_fsm = self._parent.parent
            if parent_fsm:
                parent_fsm._add_event(
                    EventType(
                        signal=Signal.CUSTOM,
                        data=FunctionFSM.FunctionFSMData(
                            signal=FunctionFSM.FunctionFSMSignal.ADD_ARGUMENT,
                            value=self._state,
                        ),
                    )
                )
            result = EventDrivenFsmReturnType.HANDLED
        else:
            result = EventDrivenFsmReturnType.HANDLED
        return result

    def dispath(self, event: EventType) -> None:
        """对外接口，立即处理事件"""
        self._parent.dispath(event)

    def _add_event(self, event: EventType) -> None:
        """内部接口，仅入队"""
        self._parent._add_event(event)

    @property
    def state(self):
        return self._state

class FunctionParser:
    """函数解析器, 进行分词, 子函数状态机管理."""

    def __init__(self):
        self.root_fsm = FunctionFSM()
        self.fsm_stack = [self.root_fsm]

    def parse(self, expr: str) -> FunctionFSM.FunctionFSMState:
        tokens = self._tokenize(expr)
        for token in tokens:
            if token == '(':
                # 新建子状态机并入栈
                new_fsm = FunctionFSM()
                self.fsm_stack[-1]._parent._add_child(new_fsm._parent)
                self.fsm_stack.append(new_fsm)
            elif token == ')':
                # 子状态机结束，触发退出
                finished_fsm = self.fsm_stack.pop()
                finished_fsm.dispath(EventType(signal=Signal.EXIT))
            elif self._is_number(token):
                # 作为参数
                self.fsm_stack[-1].dispath(EventType(
                    signal=Signal.CUSTOM,
                    data=FunctionFSM.FunctionFSMData(
                        signal=FunctionFSM.FunctionFSMSignal.ADD_ARGUMENT,
                        value=int(token)
                    )
                ))
            elif token.isidentifier():
                # 设置函数名
                self.fsm_stack[-1].dispath(EventType(
                    signal=Signal.CUSTOM,
                    data=FunctionFSM.FunctionFSMData(
                        signal=FunctionFSM.FunctionFSMSignal.SET_FUNCTION_NAME,
                        value=token
                    )
                ))
            else:
                raise ValueError(f"Unknown token: {token}")
        # 处理完毕，返回根状态
        return self.root_fsm.state

    def _tokenize(self, expr: str) -> List[str]:
        # 简单分词器，支持数字、标识符、括号
        tokens = []
        buf = ''
        for c in expr:
            if c in '()':
                if buf:
                    tokens.append(buf)
                    buf = ''
                tokens.append(c)
            elif c.isspace():
                if buf:
                    tokens.append(buf)
                    buf = ''
            else:
                buf += c
        if buf:
            tokens.append(buf)
        return tokens

    def _is_number(self, s: str) -> bool:
        try:
            int(s)
            return True
        except ValueError:
            return False

if __name__ == "__main__":
    # 测试用例
    parser = FunctionParser()
    expr = "add(add(1,2),3)"
    result = parser.parse(expr)
    print("Function name:", result.function_name)
    print("Arguments:", result.args)
    # 递归打印参数结构
    def print_args(args, indent=0):
        for arg in args:
            if isinstance(arg, FunctionFSM.FunctionFSMState):
                print("  " * indent + f"Function: {arg.function_name}")
                print_args(arg.args, indent + 1)
            else:
                print("  " * indent + f"Value: {arg}")
    print_args(result.args)
