import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, List, Callable, Optional, Protocol, Tuple, Type
from modules.core.event_driven_fsm import (
    EventDrivenFsm,
    EventType,
    Signal,
    EventDrivenFsmReturnType,
)


class TupleFSM:
    class TupleFSMSignal(Enum):
        """Signals for TupleFSM custom actions (e.g., add expression)."""

        ADD_MEMBER = auto()  # 添加元组成员

    @dataclass
    class TupleFSMState:
        """State data for TupleFSM, storing the parsed tuple members."""

        members: List[Any]

    @dataclass
    class TupleFSMData:
        signal: "TupleFSM.TupleFSMSignal"
        value: Any = None  # 可以是字符串或其他类型

    def __init__(self):
        self._parent = EventDrivenFsm(self._init_state)

    def _init_state(self, event: EventType) -> EventDrivenFsmReturnType:
        result: EventDrivenFsmReturnType = EventDrivenFsmReturnType.HANDLED
        if event.signal == Signal.ENTRY:
            self._state: TupleFSM.TupleFSMState = TupleFSM.TupleFSMState(members=[])
            self._parent.transition(self._tuple_state)
        return result

    def _tuple_state(self, event: EventType) -> EventDrivenFsmReturnType:
        result: EventDrivenFsmReturnType = EventDrivenFsmReturnType.HANDLED
        if event.signal == Signal.CUSTOM and isinstance(
            event.data, TupleFSM.TupleFSMData
        ):
            if event.data.signal == TupleFSM.TupleFSMSignal.ADD_MEMBER:
                self._state.members.append(event.data.value)
        elif event.signal == Signal.EXIT:
            # 通知上层状态机
            if self._parent.parent is None:
                raise RuntimeError("No parent FSM to return to")
            self._parent.parent.dispath(
                EventType(
                    signal=Signal.RETURN_VALUE,
                    data=self._state,  # 返回当前状态
                )
            )

        return result


class LiteralFSM:
    """字符串常量状态机"""

    class LiteralFSMSignal(Enum):
        """Signals for LiteralFSM custom actions (e.g., set string value)."""

        SET_STRING = auto()  # 设置字符串值

    @dataclass
    class LiteralFSMState:
        """State data for LiteralFSM, storing the parsed string value."""

        value: str

    @dataclass
    class LiteralFSMData:
        signal: "LiteralFSM.LiteralFSMSignal"
        value: Any = None  # 可以是字符串或其他类型

    """FSM for parsing string literals."""

    def __init__(self):
        self._parent = EventDrivenFsm(self._init_state)

    def _init_state(self, event: EventType) -> EventDrivenFsmReturnType:
        result: EventDrivenFsmReturnType = EventDrivenFsmReturnType.HANDLED
        if event.signal == Signal.ENTRY:
            self._state: LiteralFSM.LiteralFSMState = LiteralFSM.LiteralFSMState(
                value=""
            )
            self._parent.transition(self._string_state)
        return result

    def _string_state(self, event: EventType) -> EventDrivenFsmReturnType:
        result: EventDrivenFsmReturnType = EventDrivenFsmReturnType.HANDLED
        if event.signal == Signal.CUSTOM and isinstance(
            event.data, LiteralFSM.LiteralFSMData
        ):
            if event.data.signal == LiteralFSM.LiteralFSMSignal.SET_STRING:
                self._state.value = event.data.value
        elif event.signal == Signal.EXIT:
            # 通知上层状态机
            if self._parent.parent is None:
                raise RuntimeError("No parent FSM to return to")
            self._parent.parent.dispath(
                EventType(
                    signal=Signal.RETURN_VALUE,
                    data=self._state,  # 返回当前状态
                )
            )
        return result


class CompositeParser:
    """复合表达式解析器, 解析一层可嵌套对象, 返回一个FSM对象
    使用_add_event以便异步的处理事件"""

    def parse(self, expr: str) -> Optional[EventDrivenFsm]:
        i = 0
        n = len(expr)
        while i < n:
            c = expr[i]
            if c.isspace():
                i += 1
                continue
            elif c in ("'", '"'):
                # 字符串常量
                end = i + 1
                while end < n:
                    if expr[end] == c and expr[end - 1] != "\\":
                        break
                    end += 1
                value = expr[i : end + 1]
                fsm = LiteralFSM()._parent
                fsm._add_event(
                    EventType(
                        signal=Signal.CUSTOM,
                        data=LiteralFSM.LiteralFSMData(
                            signal=LiteralFSM.LiteralFSMSignal.SET_STRING,
                            value=value,
                        ),
                    )
                )
                return fsm
            elif c == "(":
                # 元组或函数
                # 判断前面是否有函数名
                j = i - 1
                while j >= 0 and expr[j].isspace():
                    j -= 1
                if j >= 0 and (expr[j].isalpha() or expr[j] == "_"):
                    # 认为是函数
                    start = j
                    while start >= 0 and (expr[start].isalnum() or expr[start] == "_"):
                        start -= 1
                    func_name = expr[start + 1 : j + 1]
                    fsm = FunctionFSM()._parent
                    fsm._add_event(
                        EventType(
                            signal=Signal.CUSTOM,
                            data=FunctionFSM.FunctionFSMData(
                                signal=FunctionFSM.FunctionFSMSignal.ADD_EXPRESSION,
                                value=func_name + expr[i:],
                            ),
                        )
                    )
                    return fsm
                else:
                    # 认为是元组
                    fsm = TupleFSM()._parent  # 你需要实现TupleFSM
                    fsm._add_event(
                        EventType(
                            signal=Signal.CUSTOM,
                            data=TupleFSM.TupleFSMData(
                                signal=TupleFSM.TupleFSMSignal.ADD_EXPRESSION,
                                value=expr[i:],
                            ),
                        )
                    )
                    return fsm
            elif c == "[":
                # 列表
                fsm = ListFSM()._parent  # 你需要实现ListFSM
                fsm._add_event(
                    EventType(
                        signal=Signal.CUSTOM,
                        data=ListFSM.ListFSMData(
                            signal=ListFSM.ListFSMSignal.ADD_EXPRESSION,
                            value=expr[i:],
                        ),
                    )
                )
                return fsm
            elif c == "{":
                # 字典
                fsm = DictFSM()._parent  # 你需要实现DictFSM
                fsm._add_event(
                    EventType(
                        signal=Signal.CUSTOM,
                        data=DictFSM.DictFSMData(
                            signal=DictFSM.DictFSMSignal.ADD_EXPRESSION,
                            value=expr[i:],
                        ),
                    )
                )
                return fsm
            else:
                # 普通标识符
                start = i
                while i < n and (expr[i].isalnum() or expr[i] == "_"):
                    i += 1
                value = expr[start:i]
                # 你可以根据需要返回一个简单的标识符FSM或直接返回值
                # 这里直接返回None或自定义FSM
                return value
            i += 1
        return None


class FunctionFSM:
    """Active Object for function parsing."""

    class FunctionFSMSignal(Enum):
        """Signals for FunctionFSM custom actions (e.g., set function name, add argument)."""

        SET_FUNCTION_NAME = auto()  # 设置函数名
        ADD_PARAM = auto()  # 添加参数

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
        if event.signal == Signal.ENTRY:
            # self._expression = ""
            pass
        elif event.signal == Signal.CUSTOM and isinstance(
            event.data, self.FunctionFSMData
        ):
            if event.data.signal == self.FunctionFSMSignal.ADD_EXPRESSION:
                # 1. find first '('
                parts = event.data.value.split("(", 1)
                if len(parts) != 2:
                    raise ValueError("Invalid function call syntax")
                self._expr_index = len(parts[0])

                # 2. set function name
                self._state.function_name = parts[0].strip()

                # 3. transition to arg list state, and add the remaining string
                self._parent.transition(self._arg_list_state)
                self._parent.dispath(
                    EventType(
                        signal=Signal.CUSTOM,
                        data=self.FunctionFSMData(
                            signal=self.FunctionFSMSignal.ADD_EXPRESSION,
                            value=parts[1].strip(),
                        ),
                    )
                )
        result = EventDrivenFsmReturnType.HANDLED
        return result

    def _arg_list_state(self, event: EventType) -> EventDrivenFsmReturnType:
        result: EventDrivenFsmReturnType = EventDrivenFsmReturnType.HANDLED

        if event.signal == Signal.ENTRY:
            pass
        elif event.signal == Signal.CUSTOM and isinstance(
            event.data, self.FunctionFSMData
        ):
            if event.data.signal == self.FunctionFSMSignal.ADD_EXPRESSION:
                expr = event.data.value
                # Start parsing the argument list
                for cur_char in expr:
                    if cur_char == " ":
                        pass
                    elif cur_char in "'\"":
                        # Literal string, add a sub-state machine to handle it.
                        leaf_fsm = LiteralFSM()._parent
                        self._parent._add_child(leaf_fsm)
                        # 将当前字符串委托给叶子节点
                        leaf_fsm.dispath(
                            EventType(
                                signal=Signal.CUSTOM,
                                data=LiteralFSM.LiteralFSMData(
                                    signal=LiteralFSM.LiteralFSMSignal.SET_STRING,
                                    value=expr,
                                ),
                            )
                        )
                        break
                    elif cur_char == "(":
                        # Function call, add a sub-state machine to handle it.
                        leaf_fsm = FunctionFSM()._parent
                        self._parent._add_child(leaf_fsm)
                        # 将当前字符串委托给叶子节点
                        leaf_fsm.dispath(
                            EventType(
                                signal=Signal.CUSTOM,
                                data=FunctionFSM.FunctionFSMData(
                                    signal=FunctionFSM.FunctionFSMSignal.ADD_EXPRESSION,
                                    value=expr,
                                ),
                            )
                        )
                        break
                    elif cur_char == ",":
                        # Comma, indicating the end of an argument, add the current argument to the list.
                        parts = expr.split(",", 1)
                        if len(parts) == 2:
                            arg = parts[0].strip()
                            if arg:
                                # Add the argument to the current function state
                                self._state.args.append(arg)
                            # Transition to the next argument
                            self._parent.dispath(
                                EventType(
                                    signal=Signal.CUSTOM,
                                    data=FunctionFSM.FunctionFSMData(
                                        signal=FunctionFSM.FunctionFSMSignal.ADD_EXPRESSION,
                                        value=parts[1].strip(),
                                    ),
                                )
                            )
                        break
                    elif cur_char == ")":
                        # Closing parenthesis, indicating the end of the argument list.
                        parts = expr.split(")", 1)
                        if len(parts) == 2:
                            arg = parts[0].strip()
                            if arg:
                                self._state.args.append(arg)
                            # Exit the state machine
                            # 通知上层状态机
                            # 1. 添加当前函数调用结果到上层状态机的参数列表
                            if self._parent.parent is None:
                                raise RuntimeError("No parent FSM to return to")
                            self._parent.parent.dispath(
                                EventType(
                                    signal=Signal.CUSTOM,
                                    data=FunctionFSM.FunctionFSMData(
                                        signal=FunctionFSM.FunctionFSMSignal.ADD_PARAM,
                                        value=self._state,
                                    ),
                                )
                            )
                            # 2. 添加剩余的expression到上层状态机
                            self._parent.parent.dispath(
                                EventType(
                                    signal=Signal.CUSTOM,
                                    data=FunctionFSM.FunctionFSMData(
                                        signal=FunctionFSM.FunctionFSMSignal.ADD_EXPRESSION,
                                        value=parts[1].strip(),
                                    ),
                                )
                            )
                        break
                    else:
                        pass
            elif event.data.signal == FunctionFSM.FunctionFSMSignal.ADD_PARAM:
                # 添加参数到当前函数调用
                self._state.args.append(event.data.value)

        elif event.signal == Signal.EXIT:
            pass

        return result

    @property
    def state(self):
        return self._state


class FunctionParser:
    """函数解析器, 进行分词, 子函数状态机管理."""

    def __init__(self):
        self._wrapper_fsm = EventDrivenFsm(self._wrapper)
        self._result: Optional[FunctionFSM.FunctionFSMState] = None

    def _wrapper(self, event: EventType) -> EventDrivenFsmReturnType:
        result = EventDrivenFsmReturnType.HANDLED
        if event.signal == Signal.CUSTOM and isinstance(
            event.data, FunctionFSM.FunctionFSMData
        ):
            if event.data.signal == FunctionFSM.FunctionFSMSignal.ADD_PARAM:
                print("Final result:", event.data.value)
                self._result = event.data.value
        return result

    """function1(abc, (1,2,3), function2(x, y))"""

    def parse(self, expr: str) -> Optional[FunctionFSM.FunctionFSMState]:
        # 1. 假设第一个Fsm一定是FunctionFSM
        leaf_fsm = FunctionFSM()._parent
        self._wrapper_fsm._add_child(leaf_fsm)

        # 2. 将当前字符串委托给叶子节点
        leaf_fsm.dispath(
            EventType(
                signal=Signal.CUSTOM,
                data=FunctionFSM.FunctionFSMData(
                    signal=FunctionFSM.FunctionFSMSignal.ADD_EXPRESSION, value=expr
                ),
            )
        )

        self._wrapper_fsm._drive()
        return self._result


if __name__ == "__main__":
    # 测试用例
    # function_parser = FunctionParser()
    # exprs = [
    #     # "func1(a, b, c)",
    #     "func3('a', func4(b, c), 'd')",
    #     # "string_join(+++, node_value(user_data_1), node_value(user_data_2), 'static string')",
    # ]
    # for expr in exprs:
    #     print(
    #         f"Parsing expression: {expr}\n    Result: {function_parser.parse(expr)}\n"
    #     )
    expr = "hahaha"
    parser = CompositeParser()
    fsm = parser.parse(expr)
    if fsm:
        fsm._drive()
        print(f"Parsed FSM: {fsm.state}")