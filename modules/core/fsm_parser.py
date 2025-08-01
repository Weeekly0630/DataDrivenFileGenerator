from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List, Callable, Optional


@dataclass
class FsmParser:
    """Generic recursive Finite State Machine Parser for parsing FSM definitions."""

    state: Optional[Callable[..., "ReturnType"]]  # The current state function to call
    children: Optional["FsmParser"]

    class ReturnType(Enum):
        """Enum to represent the return type of the FSM parser."""

        UNHANDLED = (
            auto()
        )  # Current Fsm Parser did not handle the input and further processing is needed
        HANDLED = (
            auto()
        )  # Current Fsm Parser handled the input and no further processing is needed

    def drive(self, *args, **kwargs) -> None:
        # post visit the current state
        fsm_stack: List[FsmParser] = [self]
        cur_fsm: Optional["FsmParser"] = self

        if cur_fsm.children:
            fsm_stack.append(cur_fsm.children)

        # reverse the stack to process from the last child to the first
        fsm_stack.reverse()

        # process the FSM stack
        for fsm in fsm_stack:
            # call the current state function
            if fsm.state is None:
                raise ValueError("FSM state is not set.")
            result = fsm.state(*args, **kwargs)
            if result == FsmParser.ReturnType.UNHANDLED:
                pass
            elif result == FsmParser.ReturnType.HANDLED:
                break

    def transition(self, new_state: Callable[..., "ReturnType"]) -> None:
        """Transition to a new state with optional children."""
        self.state = new_state

    def add_child(self, child: "FsmParser") -> None:
        """Add a child FSM parser to the current parser."""
        if self.children is None:
            self.children = child
        else:
            raise ValueError(
                "This FSM parser already has a child. Use a different parser for multiple children."
            )


class FunctionParser:
    """Parser for function calls in a string."""

    class ParseObjectType(Enum):
        """Enum to represent the type of parsed object."""

        FUNCTION = auto()  # Function call
        ARGUMENT = auto()

    @dataclass
    class ParseObject:
        """Object to hold the parsed function name and arguments."""

        type: "FunctionParser.ParseObjectType"
        value: Any

    class ParseState(Enum):
        INIT = auto()  # Initial state, check special characters
        FUNC_NAME = auto()  # Parsing function name
        OPEN_PAREN = auto()  # Expecting '(' after function name
        ARG = auto()  # Parsing argument value
        ARG_COMMA = auto()  # After ',', expecting next argument
        CLOSE_PAREN = auto()  # After ')', end of argument list
        END = auto()  # Parsing complete

    def __init__(self) -> None:
        self.fsm = FsmParser(state=None, children=None)

        self.cur_read_string: str = ""  # 当前读到的字符串
        self.parsed_object_list: List["FunctionParser.ParseObject"] = (
            []
        )  # 当前解析的object列表
        self.expression: str = ""  # 当前解析的表达式
        self.expression_index: int = 0  # 当前解析的表达式索引
        
    def parse(self, expression: str) -> Any:
        """Parse the given expression and return the parsed function objects."""
        self.fsm.transition(self.init_state)
        self.fsm.drive(expression)

    @staticmethod
    def raw_string_check(s: str) -> bool:
        """Check if a string is a valid raw string."""
        if s.startswith(("'", '"')) and s.endswith(("'", '"')):
            return True
        else:
            return False
    
    def get_next_char(self) -> str:
        """Get the next character in the expression, handling escape sequences."""
        return self.expression[self.expression_index] if self.expression_index < len(self.expression) else ""
        
    def init_state(self, expression: str) -> FsmParser.ReturnType:
        """Initial state of the FSM parser."""
        self.expression = expression
        self.expression_index = 0
        self.parsed_object_list.clear()
        self.cur_read_string: str = ""  # 当前读到的字符串        
        if FunctionParser.raw_string_check(self.expression) == True:
            # end
            self.fsm.transition(self.end_state)
        else:
            self.fsm.transition(self.func_name_state)
        return FsmParser.ReturnType.HANDLED

    def func_name_state(self) -> FsmParser.ReturnType:
        """State for parsing function name."""
        cur_char = self.get_next_char()
        if cur_char == "":
            # end of expression
        
    def end_state(self) -> FsmParser.ReturnType:
        """End state of the FSM parser."""
        return FsmParser.ReturnType.HANDLED
