from modules.jinja.user_func.func_handler import UserFunctionInfo
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Callable


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
    def dynamic_functions(cls, node: DataNode) -> List[UserFunctionInfo]:
        """动态数学函数（使用节点上下文）"""
        return [
            UserFunctionInfo(
                name="math:node_value",
                arg_range=(0, 0),
                description="Get current node's numeric value",
                handler=lambda: float(node.data.get("value", 0)),
            ),
            UserFunctionInfo(
                name="math:children_sum",
                arg_range=(0, 0),
                description="Sum values of all child nodes",
                handler=lambda: sum(
                    (
                        float(child.data.get("value", 0))
                        if isinstance(child, DataNode)
                        else 0
                    )
                    for child in node.children
                ),
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
