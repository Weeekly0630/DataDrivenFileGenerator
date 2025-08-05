from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, List, Callable, Optional, Protocol, Tuple
from .event_driven_fsm import *

class FunctionFSM:
    """Active Object for function parsing."""

    class FunctionFSMSignal(Enum):
        """Signals for FunctionFSM custom actions (e.g., set function name, add argument)."""

        # SET_FUNCTION_NAME = auto()
        # ADD_ARGUMENT = auto()
        ADD_IDENTIFIER = auto()

    @dataclass
    class FunctionFSMState:
        """State data for FunctionFSM, storing function name and argument list."""

        function_name: str = ""
        args: List[Any] = field(default_factory=list)

    def __init__(self) -> None:
        self._parent = EventDrivenFsm(self._init_state)

    @dataclass
    class FunctionFSMData:
        """Event data for FunctionFSM, carrying a FunctionFSMSignal and associated value."""

        signal: "FunctionFSM.FunctionFSMSignal"
        value: Any = None

    def _init_state(self, event: EventType) -> EventDrivenFsmReturnType:
        result: EventDrivenFsmReturnType
        if event.signal == Signal.ENTRY:
            # Initialize the state when entering
            self._state = self.FunctionFSMState()
            self._parent.transition(self._func_name_state)
            result = EventDrivenFsmReturnType.HANDLED
        # 处理自定义事件
        result = EventDrivenFsmReturnType.HANDLED
        return result

    def _func_name_state(self, event: EventType) -> EventDrivenFsmReturnType:
        result: EventDrivenFsmReturnType
        if event.signal == Signal.CUSTOM and isinstance(
            event.data, self.FunctionFSMData
        ):
            if event.data.signal == self.FunctionFSMSignal.ADD_IDENTIFIER:
                self._state.function_name = event.data.value
                self._parent.transition(self._arg_list_state)
        result = EventDrivenFsmReturnType.HANDLED
        return result

    def _arg_list_state(self, event: EventType) -> EventDrivenFsmReturnType:
        result: EventDrivenFsmReturnType
        if event.signal == Signal.CUSTOM and isinstance(
            event.data, self.FunctionFSMData
        ):
            if event.data.signal == self.FunctionFSMSignal.ADD_IDENTIFIER:
                self._state.args.append(event.data.value)
            result = EventDrivenFsmReturnType.HANDLED
        elif event.signal == Signal.EXIT:
            if self._parent.parent:
                self._parent.parent.dispath(
                    EventType(
                        signal=Signal.CUSTOM,
                        data=self.FunctionFSMData(
                            signal=self.FunctionFSMSignal.ADD_IDENTIFIER,
                            value=self._state,
                        ),
                    )
                )
            result = EventDrivenFsmReturnType.HANDLED
        else:
            result = EventDrivenFsmReturnType.HANDLED
        return result

    @property
    def state(self):
        return self._state


class FunctionParser:
    """函数解析器, 进行分词, 子函数状态机管理."""

    def __init__(self):
        self._wrapper_fsm = EventDrivenFsm(self._wrapper)
        self._result : Optional[FunctionFSM.FunctionFSMState] = None
        
    def _wrapper(self, event: EventType) -> EventDrivenFsmReturnType:
        result = EventDrivenFsmReturnType.HANDLED
        if event.signal == Signal.CUSTOM and isinstance(
            event.data, FunctionFSM.FunctionFSMData
        ):
            if event.data.signal == FunctionFSM.FunctionFSMSignal.ADD_IDENTIFIER:
                print("Final result:", event.data.value)
                self._result = event.data.value
        return result

    """function1(abc, (1,2,3), function2(x, y))"""

    def parse(self, expr: str) -> Optional[FunctionFSM.FunctionFSMState]:
        tokens = self._tokenize(expr)

        # 1. 初始化根 FSM
        leaf_fsm: Optional[EventDrivenFsm] = self._wrapper_fsm

        identifier_list = []

        # 2. 处理每个 token
        for index, token in enumerate(tokens):
            if token == "(":
                # Create 1 leaf FSM for the function
                new_leaf = FunctionFSM()._parent
                if leaf_fsm:
                    leaf_fsm._add_child(new_leaf)
                leaf_fsm = new_leaf
                # Add function name
                if identifier_list:
                    func_name = identifier_list.pop()
                    leaf_fsm.dispath(
                        EventType(
                            signal=Signal.CUSTOM,
                            data=FunctionFSM.FunctionFSMData(
                                signal=FunctionFSM.FunctionFSMSignal.ADD_IDENTIFIER,
                                value=func_name,
                            ),
                        )
                    )
                else:
                    raise SyntaxError("Function name expected before '('")
            elif token == ")":
                if leaf_fsm:
                    # Add last argument if exists
                    if identifier_list:
                        arg = identifier_list.pop()
                        leaf_fsm.dispath(
                            EventType(
                                signal=Signal.CUSTOM,
                                data=FunctionFSM.FunctionFSMData(
                                    signal=FunctionFSM.FunctionFSMSignal.ADD_IDENTIFIER,
                                    value=arg,
                                ),
                            )
                        )
                    # End the current leaf FSM
                    leaf_fsm.dispath(EventType(signal=Signal.EXIT))

                    leaf_fsm = leaf_fsm.parent  # Move up to parent FSM
                else:
                    raise SyntaxError("Unmatched closing parenthesis")
            elif token == ",":
                # Add argument left to ","
                if identifier_list:
                    arg = identifier_list.pop()
                    if leaf_fsm:
                        leaf_fsm.dispath(
                            EventType(
                                signal=Signal.CUSTOM,
                                data=FunctionFSM.FunctionFSMData(
                                    signal=FunctionFSM.FunctionFSMSignal.ADD_IDENTIFIER,
                                    value=arg,
                                ),
                            )
                        )
            else:
                identifier_list.append(token)
        self._wrapper_fsm._drive()
        return self._result

    def _tokenize(self, expr: str) -> List[str]:
        # 简单分词器，支持数字、标识符、括号、逗号
        tokens = []
        buf = ""
        i = 0
        while i < len(expr):
            char = expr[i]
            if char.isspace():
                # 跳过空白
                if buf:
                    tokens.append(buf)
                    buf = ""
                i += 1
                continue
            elif char in "(),":
                if buf:
                    tokens.append(buf)
                    buf = ""
                tokens.append(char)
                i += 1
            else:
                buf += char
                i += 1
        if buf:
            tokens.append(buf)
        return tokens


if __name__ == "__main__":
    # 测试用例
    function_parser = FunctionParser()
    test_expr = "func(a, b, c)"
    test_expr1 = "func1(a, func2(b, c), d)"
    print("Parsed tokens:", function_parser.parse(test_expr))
    print("Parsed tokens:", function_parser.parse(test_expr1))