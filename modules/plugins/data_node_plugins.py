from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any


class DataNodePlugin(FunctionPlugin):
    """模板插件，用于处理模板相关的用户函数"""

    @staticmethod
    def node_value(context: UserFunctionContext, key: str) -> Any:
        """获取当前数据节点的值"""
        return context.cur_node.data.get(key)

    @staticmethod
    def node_value_validator() -> UserFunctionValidator:
        validator = UserFunctionValidator()
        validator.add_param_check_validator(1, 1)
        return validator

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        """返回插件提供的函数列表"""
        return [
            UserFunctionInfo(
                name="node_value",
                description="Get the value of a data node by its key",
                handler=cls.node_value,
                validator=cls.node_value_validator(),
            )
        ]

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
