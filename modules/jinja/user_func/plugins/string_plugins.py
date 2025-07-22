from modules.core import DataHandler
from modules.jinja.user_func.func_handler import UserFunctionInfo, UserFunctionContext
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Callable, Any


class StringPlugin(FunctionPlugin):
    """字符串操作插件"""

    @classmethod
    def functions(cls) -> List[UserFunctionInfo]:

        def join_string(
            context: UserFunctionContext, *args
        ) -> str:
            s = args[0]
            l = args[1:]
            return str(s).join([str(e) for e in l])

        return [
            UserFunctionInfo(
                name="string:join",
                arg_range=(2, 1000),
                description="string:join(join_string: str, list: List): Join a list with string",
                handler=join_string,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        pass

    @classmethod
    def on_plugin_unload(cls):
        pass
