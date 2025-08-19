from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any, Union, Optional, Callable
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase, auto_register_factories

from modules.utils.type_classes.xdm_a import XdmA, XdmAttribute


class XdmPlugin(FunctionPlugin):

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        info_funcs = auto_register_factories(XdmA)[0]
        xdm_attr_funcs = auto_register_factories(XdmAttribute)[0]
        
        infos = info_funcs + xdm_attr_funcs
        
        return infos

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass


if __name__ == "__main__":
    # 仅在直接运行此文件时执行的代码
    pass
