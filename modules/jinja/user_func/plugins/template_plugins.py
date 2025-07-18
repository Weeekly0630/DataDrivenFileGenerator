from modules.core import DataHandler
from modules.jinja.user_func.func_handler import UserFunctionInfo, UserFunctionContext
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Callable, Any


class MathUtilsPlugin(FunctionPlugin):
    """数学工具插件，包含静态和动态函数"""

    @classmethod
    def static_functions(cls) -> List[UserFunctionInfo]:
        """静态数学函数"""
        return [
            UserFunctionInfo(
                name="math:square",
                arg_range=(1, 1),
                description="Calculate the square of a number",
                handler=lambda x: x * x,
            ),
            UserFunctionInfo(
                name="math:sum",
                arg_range=(2, None),
                description="Sum all arguments",
                handler=lambda *args: sum(args),
            ),
        ]

    @classmethod
    def dynamic_functions(cls) -> List[UserFunctionInfo]:
        """动态数学函数（使用节点上下文）同时使用工厂方法"""

        def node_value(context: UserFunctionContext, file_path: str) -> Any:
            find_nodes = context.data_handler.find_by_file_path(context.node, file_path)
            if len(find_nodes) > 0:
                target = find_nodes[0]
                return target.data.get("value", None)
            else:
                return None

        def children_sum(context: UserFunctionContext) -> str:
            return "sum"

        return [
            UserFunctionInfo(
                name="math:node_value",
                arg_range=(1, 1),
                description="Get node value by file_path",
                handler=node_value,
            ),
            UserFunctionInfo(
                name="math:children_sum",
                arg_range=(0, 0),
                description="Sum values of all child nodes",
                handler=children_sum,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        print(
            f"MathUtilsPlugin loaded with {len(cls.static_functions())} static functions"
        )

    @classmethod
    def on_plugin_unload(cls):
        print("MathUtilsPlugin unloaded")
