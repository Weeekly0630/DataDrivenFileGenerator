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
        """
        自动注册机制说明：
        1. 自动递归遍历 TemplatePlugin 及其所有嵌套类，收集所有以 _create 结尾的静态方法。
        2. 自动查找同名 _validator 方法（只在 TemplatePlugin 本身查找），如有则注册为 validator。
        3. 注册时函数名为 "templateplugin_嵌套类名_方法名"，保证唯一性。
        4. 支持多级嵌套，新增类型无需修改注册逻辑。
        5. validator 必须为 UserFunctionValidator 实例或 None。
        """
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
