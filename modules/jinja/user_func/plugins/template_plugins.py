from modules.core import DataHandler
from modules.jinja.user_func.func_handler import UserFunctionInfo, UserFunctionContext
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Callable, Any


class MathUtilsPlugin(FunctionPlugin):
    """数学工具插件"""

    @classmethod
    def functions(cls) -> List[UserFunctionInfo]:

        def node_value(context: UserFunctionContext, file_path: str) -> Any:
            find_nodes = context.data_handler.find_by_file_path(context.node, file_path)
            if len(find_nodes) > 0:
                target = find_nodes[0]
                return target.data.get("value", "")
            else:
                return ""

        def children_sum(context: UserFunctionContext) -> str:
            return "sum"

        def sum_list(context: UserFunctionContext, numbers: List[float]) -> float:
            """计算数字列表的和"""
            return sum(numbers)
        
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
            UserFunctionInfo(
                name="math:sum",
                arg_range=(1, 1),
                description="Calculate the sum of a list of numbers",
                handler=sum_list,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        pass
        # print("MathUtilsPlugin loaded")

    @classmethod
    def on_plugin_unload(cls):
        pass
        # print("MathUtilsPlugin unloaded")
