import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from typing import Any, Callable, Dict, List, Union, Optional, Type
from dataclasses import dataclass
from modules.node.data_node import DataNode
from modules.core import DataHandler, TemplateHandler
from pathlib import Path
import importlib


@dataclass
class UserFunctionValidator:
    """A class for validating user-defined functions."""

    validate_function_list: List[Callable[..., bool]]  # List of validation functions

    def add_validator(
        self,
        validator: Callable[
            ...,
            bool,
        ],
    ) -> None:
        """Add a new validator to the list."""
        self.validate_function_list.append(validator)

    def add_param_check_validator(
        self, min_args: int = 0, max_args: Optional[int] = None
    ) -> None:
        """Add a parameter count validation function."""

        def param_len_check(*args, **kwargs) -> bool:
            # min check
            if len(args) < min_args:
                raise ValueError(
                    f"Function requires at least {min_args} arguments, got {len(args)}"
                )
            # max check
            if max_args is not None and len(args) > max_args:
                raise ValueError(
                    f"Function allows at most {max_args} arguments, got {len(args)}"
                )

            return True

        self.add_validator(param_len_check)

    def validate(self, *args, **kwargs) -> bool:
        """Validate the function arguments using all validators.
        Returns True if all pass, or error message string if failed.
        """
        for validator in self.validate_function_list:
            try:
                validator(*args, **kwargs)
            except Exception as e:
                raise ValueError(
                    f"Validation failed for {validator.__name__}: {str(e)}"
                )

        return True


# 插件接口
class FunctionPlugin:
    """插件基类，支持静态和动态函数"""

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        """返回插件提供的函数列表"""
        return []

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass


@dataclass
class UserFunctionInfo:
    """A class representing user function information."""

    name: str
    description: str
    handler: Callable[["UserFunctionContext", Any], Any]
    validator: Optional[UserFunctionValidator] = None

    def __post_init__(self):
        import re

        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", self.name):
            raise ValueError(f"函数名不合法: {self.name}")


@dataclass
class UserFunctionContext:
    """Context for user function resolution."""

    cur_node: DataNode  # Current data node
    data_handler: DataHandler  # Data handler instance
    template_handler: TemplateHandler  # Template handler instance


class UserFunctionResolver:
    """User-defined function resolver."""

    def __init__(self, plugins_dirs: List[str]) -> None:
        self.functions: Dict[str, UserFunctionInfo] = {}
        self.plugin_classes: List[Type[FunctionPlugin]] = []

        # 初始化时加载所有插件
        for plugins_dir in plugins_dirs:
            self._load_plugins(plugins_dir)
        # 收集所有函数
        self._collect_functions()

    def parse(self, expression: str, context: "UserFunctionContext") -> Any:
        """
        FSM-based parser for single-layer function calls: func(arg1, arg2)
        Uses Enum for states and provides detailed descriptions for each state.
        Returns the result of the function call, or None if not valid.
        """
        class ParseState(Enum):
            INIT = auto()  # Initial state, check special characters
            FUNC_NAME = auto()  # Parsing function name
            OPEN_PAREN = auto()  # Expecting '(' after function name
            ARG = auto()  # Parsing argument value
            ARG_COMMA = auto()  # After ',', expecting next argument
            CLOSE_PAREN = auto()  # After ')', end of argument list
            END = auto()  # Parsing complete

       
        def validate_function_name(name: str) -> bool:
            """Validate function name against regex."""
            import re
            return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name))
        
        state = ParseState.INIT
        result = None

        """
        add(1, 2)
        add0(add1(1,2), 3) 先解析add1(1,2)，再解析add0(add1(1,2), 3)
        """
        parse_object_list: List[ParseObject] = []  # 用于存储解析的函数和参数
        def parse_object_list_reset() -> None:
            """Reset the parse object list."""
            nonlocal parse_object_list
            parse_object_list = []
        def parse_object_list_append(obj: ParseObject) -> None:
            """Append a parse object to the list."""
            nonlocal parse_object_list
            if not isinstance(obj, ParseObject):
                raise TypeError(f"Expected ParseObject, got {type(obj)}")
            parse_object_list.append(obj)
        def parse_object_list_pop() -> ParseObject:
            """Pop the last parse object from the list."""
            nonlocal parse_object_list
            if parse_object_list:
                return parse_object_list.pop()
            else:
                raise IndexError("Parse object list is empty.")
            
        def parse_function_object_resolve() -> tuple[str, List[Any], Any]:
            """Resolve the last function object in the parse object list."""
            nonlocal parse_object_list
            if not parse_object_list:
                raise ValueError("Parse object list is empty.")
            # find last function object
            for i in range(len(parse_object_list) - 1, -1, -1):
                if parse_object_list[i].type == ParseObjectType.FUNCTION:
                    func_obj = parse_object_list[i]
                    break
            # if not found, raise error
            if not func_obj:
                raise ValueError("No function object found in parse object list.")
            # get args
            args = []
            for j in range(i + 1, len(parse_object_list)):
                if parse_object_list[j].type == ParseObjectType.ARGUMENT:
                    args.append(parse_object_list[j].value)
            # remove function object and args from list
            parse_object_list = parse_object_list[:i]
            # resolve function
            result = self.resolve(func_obj.value, context, *args)
            # append result to parse object list
            parse_object_list_append(ParseObject(type=ParseObjectType.ARGUMENT, value=result))

            return func_obj.value, args, result
        # # 函数名栈
        # function_name_list: List[str] = []
        # def function_name_list_reset() -> None:
        #     """Reset the function name list."""
        #     nonlocal function_name_list
        #     function_name_list = []
        # def function_name_list_append(name: str) -> None:
        #     """Append a function name to the list."""
        #     nonlocal function_name_list
        #     if not validate_function_name(name):
        #         raise ValueError(f"Invalid function name: {name}")
        #     function_name_list.append(name)
        # def function_name_list_pop() -> str:
        #     """Pop the last function name from the list."""
        #     nonlocal function_name_list
        #     if function_name_list:
        #         return function_name_list.pop()
        #     else:
        #         raise IndexError("Function name list is empty.")
            
        # arg_list: List[Any] = []  # 用于存储每个函数的参数列表
        # def arg_list_reset() -> None:
        #     """Reset the argument list."""
        #     nonlocal arg_list
        #     arg_list = []
        # def arg_list_append(arg: Any) -> None:
        #     """Append an argument to the argument list."""
        #     nonlocal arg_list
        #     if raw_string_check(arg):
        #         arg = arg[1:-1]  # Remove quotes from raw strings
        #     arg_list.append(arg)
        # def arg_list_pop() -> Any:
        #     """Pop the last argument from the argument list."""
        #     nonlocal arg_list
        #     if arg_list:
        #         return arg_list.pop()
            
        cur_char_index = 0
        char_index_max = len(expression)
        
        cur_read_string: str = "" # 记录当前读到的字符串
        def cur_read_string_reset() -> None:
            """Reset the current read string."""
            nonlocal cur_read_string
            cur_read_string = ""
        def cur_read_string_append(c: str) -> None:
            """Append a character to the current read string."""
            nonlocal cur_read_string
            cur_read_string += c
        def cur_read_string_get() -> str:
            """Get the current read string."""
            nonlocal cur_read_string
            return cur_read_string
        def get_next_char() -> str:
            """Get the next character from the expression."""
            nonlocal cur_char_index
            nonlocal char_index_max
            nonlocal expression
        
            cur_char = expression[cur_char_index] if cur_char_index < char_index_max else ""
            cur_char_index += 1
            return cur_char
        
        def transfer_state_by_char(cur_char: str) -> None:
            """Transfer state based on the current character."""
            nonlocal state
            if cur_char == "(":
                state = ParseState.OPEN_PAREN
            elif cur_char == ")":
                state = ParseState.CLOSE_PAREN
            
        while state != ParseState.END:
            if state == ParseState.INIT:
                if raw_string_check(expression):
                    state = ParseState.END
                    expression = expression[1:-1]  # Remove quotes
                    result = expression
                else:
                    cur_read_string_reset()
                    state = ParseState.FUNC_NAME
            else:
                if state == ParseState.FUNC_NAME:
                    cur_char = get_next_char()
                    if cur_char == "":
                        state = ParseState.END
                    else:
                        if cur_char == "(":
                            # End of function name, move to next state
                            f_name = cur_read_string_get().strip()
                            parse_object_list_append(ParseObject(type=ParseObjectType.FUNCTION, value=f_name))
                            cur_read_string_reset()
                            state = ParseState.OPEN_PAREN
                        else:
                            cur_read_string_append(cur_char)
                            
                elif state == ParseState.OPEN_PAREN:
                    cur_char = get_next_char()
                    if cur_char == "":
                        state = ParseState.END
                    else:
                        if cur_char == ")" or cur_char == ",":
                            # Comma, expect next argument
                            arg = cur_read_string_get()
                            arg = arg.strip()
                            parse_object_list_append(ParseObject(type=ParseObjectType.ARGUMENT, value=arg))
                            cur_read_string_reset()
                            if cur_char == ")":
                                state = ParseState.CLOSE_PAREN
                        elif cur_char == "(":
                            # Nested function call, do the same as FUNC_NAME
                            f_name = cur_read_string_get().strip()
                            parse_object_list_append(ParseObject(type=ParseObjectType.FUNCTION, value=f_name))
                            cur_read_string_reset()
                        else:
                            cur_read_string_append(cur_char)
                elif state == ParseState.CLOSE_PAREN:
                    # call 1 function
                    f_n, f_args, f_result = parse_function_object_resolve() 
                    print(f"Function name: {f_n}, Args: {f_args}, Result: {f_result}")
                    # Start a new function call
                    cur_read_string_append(f_result)
                    state = ParseState.FUNC_NAME
                elif state == ParseState.END:
                    break
        return result
        # func_name = ""
        # args = []
        # cur_arg = ""
        # i = 0
        # n = len(expression)
        # while i < n:
        #     c = expression[i]
        #     # INIT: Skip whitespace, look for start of function name
        #     if state == ParseState.INIT:
        #         if c.isspace():
        #             i += 1
        #             continue
        #         elif c.isalpha() or c == "_":
        #             func_name += c
        #             state = ParseState.FUNC_NAME
        #         else:
        #             return None
        #     # FUNC_NAME: Collect valid function name characters, look for '('
        #     elif state == ParseState.FUNC_NAME:
        #         if c.isalnum() or c == "_":
        #             func_name += c
        #         elif c == "(":
        #             state = ParseState.OPEN_PAREN
        #         elif c.isspace():
        #             pass
        #         else:
        #             return None
        #     # OPEN_PAREN: Skip whitespace, look for arguments or ')'
        #     elif state == ParseState.OPEN_PAREN:
        #         if c.isspace():
        #             pass
        #         elif c == ")":
        #             state = ParseState.CLOSE_PAREN
        #         else:
        #             cur_arg += c
        #             state = ParseState.ARG
        #     # ARG: Collect argument characters until ',' or ')'
        #     elif state == ParseState.ARG:
        #         if c == ",":
        #             args.append(cur_arg.strip())
        #             cur_arg = ""
        #             state = ParseState.ARG_COMMA
        #         elif c == ")":
        #             args.append(cur_arg.strip())
        #             cur_arg = ""
        #             state = ParseState.CLOSE_PAREN
        #         else:
        #             cur_arg += c
        #     # ARG_COMMA: Skip whitespace, expect next argument
        #     elif state == ParseState.ARG_COMMA:
        #         if c.isspace():
        #             pass
        #         else:
        #             cur_arg += c
        #             state = ParseState.ARG
        #     # CLOSE_PAREN: Skip whitespace, parsing complete
        #     elif state == ParseState.CLOSE_PAREN:
        #         if c.isspace():
        #             pass
        #         else:
        #             state = ParseState.END
        #     if state == ParseState.END:
        #         break
        #     i += 1
        # if state not in [ParseState.CLOSE_PAREN, ParseState.END] or not func_name:
        #     return None
        # # Parse arguments to int/float if possible
        # parsed_args = []
        # for arg in args:
        #     arg = arg.strip()
        #     if not arg:
        #         continue
        #     try:
        #         if "." in arg:
        #             parsed_args.append(float(arg))
        #         else:
        #             parsed_args.append(int(arg))
        #     except ValueError:
        #         # Remove quotes if present
        #         if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
        #             parsed_args.append(arg[1:-1])
        #         else:
        #             parsed_args.append(arg)
        # return self.resolve(func_name, context, *parsed_args)

    def resolve(
        self, func_name: str, context: UserFunctionContext, *args, **kwargs
    ) -> Any:
        """
        Resolve a function by its name.
        Calls the function handler with the provided context.
        """

        if func_name not in self.functions:
            raise ValueError(f"Function '{func_name}' not found in resolver.")
        else:
            info = self.functions[func_name]
            handler: Callable[["UserFunctionContext", Any], Any] = info.handler
            validator: Optional[UserFunctionValidator] = info.validator

            try:
                if validator:
                    result = validator.validate(*args, **kwargs)
                    if result is not True:
                        raise ValueError(
                            f"Function '{func_name}' validation failed: {result}"
                        )
                return handler(context, *args, **kwargs)
            except Exception as e:
                raise ValueError(f"Function '{func_name}' execution error: {e}")

    @staticmethod
    def _serialize_function_info(info: UserFunctionInfo, indent: int) -> str:
        validator_status = "Yes" if info.validator else "No"
        result: str = (
            f"{' ' * indent}Name: {info.name}\n"
            f"{' ' * indent}  Description: {info.description}\n"
            f"{' ' * indent}  Validator: {validator_status}"
        )
        return result

    def show_function_info(self) -> str:
        result = ""
        for key, value in self.functions.items():
            result += self._serialize_function_info(value, indent=0) + "\n\n"
        return result

    def _collect_functions(self):
        """收集所有插件的静态函数"""
        # 收集插件静态函数
        plugin = {}
        for plugin_class in self.plugin_classes:
            try:
                for func_info in plugin_class.functions():
                    # 防止函数名冲突
                    if func_info.name in plugin:
                        print(
                            f"Warning: Duplicate static function name '{func_info.name}' in plugin {plugin_class.__name__} and {plugin[func_info.name].name}"
                        )
                    else:
                        plugin[func_info.name] = func_info
            except Exception as e:
                print(
                    f"Error collecting static functions from {plugin_class.__name__}: {str(e)}"
                )

        # 合并所有静态函数
        self.functions = {**plugin}

    def _load_plugins(self, plugins_dir: str) -> None:
        """扫描并加载插件目录中的所有有效插件"""
        plugins_path = Path(plugins_dir)

        if not plugins_path.exists():
            os.makedirs(plugins_path, exist_ok=True)
            return

        # 确保插件目录在Python路径中
        if str(plugins_path) not in sys.path:
            sys.path.append(str(plugins_path))

        # 扫描所有.py文件（递归，排除__init__.py）
        loaded_modules = set()
        for file_path in plugins_path.glob("**/*.py"):
            if file_path.name == "__init__.py":
                continue

            # Compute module name relative to plugins_path
            rel_path = file_path.relative_to(plugins_path)
            module_name = ".".join(rel_path.with_suffix("").parts)
            try:
                # 防止重复加载
                if module_name in loaded_modules:
                    continue

                module = importlib.import_module(module_name)
                loaded_modules.add(module_name)
                self._register_plugin(module)
            except Exception as e:
                print(f"Failed to load plugin {module_name}: {str(e)}")

    def _register_plugin(self, module):
        """注册插件模块"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            if (
                isinstance(attr, type)
                and issubclass(attr, FunctionPlugin)
                and attr != FunctionPlugin
            ):

                plugin_class = attr
                try:
                    # 调用插件初始化方法
                    plugin_class.on_plugin_load()
                    self.plugin_classes.append(plugin_class)
                    print(f"Loaded plugin: {plugin_class.__name__}")
                except Exception as e:
                    print(
                        f"Error initializing plugin {plugin_class.__name__}: {str(e)}"
                    )


if __name__ == "__main__":
    # Simple functional test for UserFunctionResolver.parse

    from types import SimpleNamespace

    class DummyContext:
        pass

    class DummyPlugin(FunctionPlugin):
        @classmethod
        def functions(cls):
            validator = UserFunctionValidator(validate_function_list=[])
            validator.add_param_check_validator(min_args=2, max_args=2)
            return [
                UserFunctionInfo(
                    name="add",
                    description="Add two numbers",
                    handler=lambda ctx, *args: int(args[0]) + int(args[1]),
                    validator=validator,
                ),
                UserFunctionInfo(
                    name="mul",
                    description="Multiply two numbers",
                    handler=lambda ctx, *args: args[0] * args[1],
                    validator=validator,
                ),
            ]

    # Setup resolver with dummy plugin
    resolver = UserFunctionResolver(plugins_dirs=[])
    resolver.plugin_classes.append(DummyPlugin)
    resolver._collect_functions()

    print(resolver.show_function_info())
    # Use a minimal UserFunctionContext for testing
    from modules.node.data_node import DataNode
    from modules.core import DataHandler, TemplateHandler

    # Use actual classes with minimal valid implementations for testing
    from modules.node.data_node import DataNode
    from modules.core import DataHandler, TemplateHandler

    class DummyDataNode(DataNode):
        pass

    class DummyDataHandler(DataHandler):
        def __init__(self, config=None):
            pass

        def create_data_tree(self, config):
            return []

    class DummyTemplateHandler(TemplateHandler):
        def __init__(self, config=None):
            pass

        def render(self, template_path: str, data: dict):
            return ""

    dummy_context = UserFunctionContext(
        cur_node=DummyDataNode(data={}, name="dummy"),
        data_handler=DummyDataHandler(),
        template_handler=DummyTemplateHandler(),
    )

    # Test simple and recursive calls
    print("add(2, 3) =", resolver.parse("add(2, 3)", dummy_context))  # Should print 5
    print(
        "mul(add(2, 3), 4) =", resolver.parse("mul(add(2, 3), 4)", dummy_context)
    )  # Should print 20

    # --- Validator Test ---
    validator = UserFunctionValidator(validate_function_list=[])
    validator.add_param_check_validator(min_args=2, max_args=2)

    print("add(2) should fail validation:")

    try:
        print(resolver.parse("add(2， 3)", dummy_context))
        print(resolver.parse("add bcd", dummy_context))
    except ValueError as e:
        print(f"Validation error: {e}")
