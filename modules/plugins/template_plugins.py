from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any

class TemplatePlugin(FunctionPlugin):
    """模板插件，用于处理模板相关的用户函数"""
    
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
