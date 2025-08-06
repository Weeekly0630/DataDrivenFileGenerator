from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any
from modules.node.data_node import DataNode


class DataNodePlugin(FunctionPlugin):
    """模板插件，用于处理模板相关的用户函数"""

    @staticmethod
    def node_value(context: UserFunctionContext, key: str, node_path: str = "") -> Any:
        """获取数据节点的值"""
        result: Any = None
        if node_path != "":
            target_nodes: List[DataNode] = DataNodePlugin.find_node_by_file_path(
                context, node_path
            )
            if len(target_nodes) == 1:
                result = target_nodes[0].data.get(key)
            elif len(target_nodes) > 1:
                result = [
                    node.data.get(key) for node in target_nodes if key in node.data
                ]
        else:
            result = context.cur_node.data.get(key)
        return result

    @staticmethod
    def node_value_validator() -> UserFunctionValidator:
        validator = UserFunctionValidator()
        validator.add_param_check_validator(1, 2)
        return validator

    @staticmethod
    def find_node_by_file_path(
        context: UserFunctionContext, file_path: str
    ) -> List[DataNode]:
        """根据文件路径查找数据节点"""
        from modules.yaml.yaml_handler import YamlDataTreeHandler

        if not isinstance(context.data_handler, YamlDataTreeHandler):
            raise ValueError("Unsupported data handler for file path lookup")

        # 使用数据处理器的查找方法
        return context.data_handler.find_node_by_path(context.cur_node, file_path)

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        """返回插件提供的函数列表"""
        return [
            UserFunctionInfo(
                name="node_value",
                description="Get the value of a data node by its key",
                handler=cls.node_value,
                validator=cls.node_value_validator(),
            ),
            UserFunctionInfo(
                name="find_node_by_file_path",
                description="Find a data node by its file path",
                handler=cls.find_node_by_file_path,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
