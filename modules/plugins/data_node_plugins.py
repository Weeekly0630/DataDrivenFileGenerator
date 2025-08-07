from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any, Union, Optional, Callable
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase, auto_register_factories
from modules.node.data_node import DataNode


class Node:
    """"""

    class Value:
        """引用节点值"""

        @dataclass
        class MetaData(MetaBase):
            """引用节点值的元数据"""

            value: Any  # 引用的值，可以是任意类型

        @staticmethod
        def create(
            context: UserFunctionContext, key: str, file_pattern: str = ""
        ) -> "Node.Value.MetaData":
            """获取数据节点的值"""
            result: Any = None
            if file_pattern != "":
                target_nodes: List[DataNode] = Node.Find.create(
                    context, file_pattern
                ).results
                if len(target_nodes) == 1:
                    result = target_nodes[0].data.get(key)
                elif len(target_nodes) > 1:
                    result = [
                        node.data.get(key) for node in target_nodes if key in node.data
                    ]
            else:
                result = context.cur_node.data.get(key)
            return Node.Value.MetaData(value=result)

    class Find:
        @dataclass
        class MetaData(MetaBase):
            """查找数据节点的结果"""

            results: List[DataNode] = field(default_factory=list)

        @staticmethod
        def create(
            context: UserFunctionContext, file_pattern: str
        ) -> "Node.Find.MetaData":
            """根据文件名模式查找数据节点"""
            from modules.yaml.yaml_handler import YamlDataTreeHandler

            if not isinstance(context.data_handler, YamlDataTreeHandler):
                raise ValueError("Unsupported data handler for file path lookup")

            # 使用数据处理器的查找方法
            return Node.Find.MetaData(
                results=context.data_handler.find_node_by_path(
                    context.cur_node, file_pattern
                )
            )


class DataNodePlugin(FunctionPlugin):
    """模板插件，用于处理模板相关的用户函数"""

    # @staticmethod
    # def node_value(context: UserFunctionContext, key: str, node_path: str = "") -> Any:
    #     """获取数据节点的值"""
    #     result: Any = None
    #     if node_path != "":
    #         target_nodes: List[DataNode] = DataNodePlugin.find_node_by_file_path(
    #             context, node_path
    #         )
    #         if len(target_nodes) == 1:
    #             result = target_nodes[0].data.get(key)
    #         elif len(target_nodes) > 1:
    #             result = [
    #                 node.data.get(key) for node in target_nodes if key in node.data
    #             ]
    #     else:
    #         result = context.cur_node.data.get(key)
    #     return result

    # @staticmethod
    # def node_value_validator() -> UserFunctionValidator:
    #     validator = UserFunctionValidator()
    #     validator.add_param_check_validator(1, 2)
    #     return validator

    # @staticmethod
    # def find_node_by_file_path(
    #     context: UserFunctionContext, file_path: str
    # ) -> List[DataNode]:
    #     """根据文件路径查找数据节点"""
    #     from modules.yaml.yaml_handler import YamlDataTreeHandler

    #     if not isinstance(context.data_handler, YamlDataTreeHandler):
    #         raise ValueError("Unsupported data handler for file path lookup")

    #     # 使用数据处理器的查找方法
    #     return context.data_handler.find_node_by_path(context.cur_node, file_path)

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        info_funcs = auto_register_factories(Node)
        # 你还可以合并手写的其它函数
        return info_funcs

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
