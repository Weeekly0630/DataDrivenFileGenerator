from modules.core import DataHandler
from modules.jinja.user_func.func_handler import UserFunctionInfo
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Callable


class DataNodePlugin(FunctionPlugin):
    """数据节点相关操作"""

    @classmethod
    def static_functions(cls) -> List[UserFunctionInfo]:
        """静态数学函数"""
        return []

    @classmethod
    def dynamic_functions(
        cls, node: DataNode, data_handler: DataHandler
    ) -> List[UserFunctionInfo]:
        """动态数学函数（使用节点上下文）"""
        return [
            UserFunctionInfo(
                name="dataNode:get_rel_path",
                arg_range=(1, 1),
                description="Get relative path using file path pattern and return the datanode path",
                handler=lambda file_path: data_handler.find_by_file_path(
                    node, file_path
                )[0].get_relative_path(node),
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        pass

    @classmethod
    def on_plugin_unload(cls):
        pass
