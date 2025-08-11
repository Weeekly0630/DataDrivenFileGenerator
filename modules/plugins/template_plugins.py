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

class TemplatePlugin(FunctionPlugin):
    """模板插件，用于处理模板相关的用户函数"""
    
    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        info_funcs = []

        
        return info_funcs

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
