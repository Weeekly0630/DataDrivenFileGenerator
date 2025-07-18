from modules.core import DataHandler
from modules.jinja.user_func.func_handler import UserFunctionInfo, UserFunctionContext
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Callable


class DataNodePlugin(FunctionPlugin):
    """数据节点相关操作"""

    @classmethod
    def static_functions(cls) -> List[UserFunctionInfo]:
        """静态数学函数"""
        return []

    @staticmethod
    def _get_targets(node, data_handler: DataHandler, file_path: str) -> List[DataNode]:
        target_nodes = data_handler.find_by_file_path(node, file_path)
        if len(target_nodes) == 0:
            raise ValueError(f"Pattern {file_path} for node {node.name} finds nothing.")
        elif len(target_nodes) > 1:
            raise ValueError(
                f"Pattern {file_path} for node {node.name} finds more than one node."
            )

        return target_nodes

    @classmethod
    def dynamic_functions(
        cls
    ) -> List[UserFunctionInfo]:
        
        def get_abs_path(context: UserFunctionContext) -> str:
            return context.node.get_absolute_path()

        def get_rel(context: UserFunctionContext, file_path: str) -> str:
            target = DataNodePlugin._get_targets(
                context.node, context.data_handler, file_path
            )[0]
            rel_path = target.get_relative_path(context.node)
            # 直接将最右侧的 '/' 右侧的名字换成name
            parts = rel_path.rsplit("/")
            if len(parts) > 1:
                parts[-1] = target.data.get("name")
            return "/".join(parts)

        def get_attr(context: UserFunctionContext, file_path: str, attr: str) -> str:
            target = DataNodePlugin._get_targets(
                context.node, context.data_handler, file_path
            )[0]
            return str(target.data.get(attr))

        """动态数学函数（使用节点上下文）"""
        return [
            UserFunctionInfo(
                name="dataNode:get_rel_path",
                arg_range=(1, 1),
                description="dataNode:get_rel_path(file_path: str): Get relative path using file path pattern and return the datanode path",
                handler=get_rel,
            ),
            UserFunctionInfo(
                name="dataNode:get_attr",
                arg_range=(2, 2),
                description="dataNode:get_attr(file_path: str, attr: str): Get attribute from a file path",
                handler=get_attr,
            ),
            UserFunctionInfo(
                name="dataNode:get_abs_path",
                arg_range=(0, 0),
                description="dataNode:get_abs_path(): Get current node absolute path.",
                handler=get_abs_path,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        pass

    @classmethod
    def on_plugin_unload(cls):
        pass
