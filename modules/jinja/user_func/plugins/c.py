from modules.core import DataHandler
from modules.jinja.user_func.func_handler import UserFunctionInfo, UserFunctionContext
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Callable, Any


class CPlugin(FunctionPlugin):
    """C模板插件, 用于生成处理所有C语言相关的模板"""

    @staticmethod
    def macro_define_info_init(
        context: UserFunctionContext, macro_name: str, macro_value: str
    ) -> Any:
        """初始化C语言宏定义模板数据字典"""
        return {
            "name": macro_name,
            "value": macro_value,
        }

    @staticmethod
    def macro_include_info_init(
        context: UserFunctionContext, file_name: str, is_system: bool = False
    ) -> Any:
        """初始化C语言include信息数据字典"""
        return {
            "file_name": file_name,
            "is_system": is_system,
        }

    @staticmethod
    def macro_if_info_init(
        context: UserFunctionContext,
        conditions: list,
        contents: list,
        else_content: Any = None,
    ) -> Any:
        """初始化C语言if宏信息数据字典"""
        return {
            "conditions": conditions,
            "contents": contents,
            "else_content": else_content,
        }

    @staticmethod
    def macro_conditional_include_info_init(
        context: UserFunctionContext,
        includes: list,
        include_condition: str = "",
        else_content: Any = None,
    ) -> Any:
        """复合C语言条件include信息数据字典"""
        return CPlugin.macro_if_info_init(
            context=context,
            conditions=[include_condition],
            contents=[
                CPlugin.macro_include_info_init(context=context, file_name=include)
                for include in includes
            ],
        )

    @classmethod
    def functions(cls) -> List[UserFunctionInfo]:
        return [
            UserFunctionInfo(
                name="c:macro_define_info_init",
                arg_range=(2, 2),
                description="生成C语言宏定义数据结构",
                handler=cls.macro_define_info_init,
            ),
            UserFunctionInfo(
                name="c:macro_include_info_init",
                arg_range=(2, 3),
                description="生成C语言include信息数据结构",
                handler=cls.macro_include_info_init,
            ),
            UserFunctionInfo(
                name="c:macro_if_info_init",
                arg_range=(2, 3),
                description="生成C语言if宏信息数据结构",
                handler=cls.macro_if_info_init,
            ),
            UserFunctionInfo(
                name="c:macro_conditional_include_info_init",
                arg_range=(1, 4),
                description="生成C语言条件include信息数据结构（适配macro_conditional_include模板）",
                handler=cls.macro_conditional_include_info_init,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        print("MathUtilsPlugin loaded")

    @classmethod
    def on_plugin_unload(cls):
        print("MathUtilsPlugin unloaded")
