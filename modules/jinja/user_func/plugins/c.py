from modules.core import DataHandler
from modules.jinja.user_func.func_handler import UserFunctionInfo, UserFunctionContext
from modules.jinja.user_func.resolver import FunctionPlugin
from modules.node.data_node import DataNode
from typing import List, Any


class CPlugin(FunctionPlugin):
    """C模板插件, 用于生成处理所有C语言相关的模板"""

    # =========================
    # 宏定义相关静态方法
    # =========================
    @staticmethod
    def macro_define_info_init(
        context: UserFunctionContext, macro_name: str, macro_value: str
    ) -> Any:
        """
        初始化C语言宏定义模板数据字典。

        Args:
            context: 用户函数上下文
            macro_name: 宏名称
            macro_value: 宏值

        Returns:
            dict: 宏定义数据结构
        """
        return {
            "name": macro_name,
            "value": macro_value,
        }

    # =========================
    # include相关静态方法
    # =========================
    @staticmethod
    def macro_include_info_init(
        context: UserFunctionContext, file_name: str, is_system: bool = False
    ) -> Any:
        """
        初始化C语言include信息数据字典。

        Args:
            context: 用户函数上下文
            file_name: 文件名
            is_system: 是否为系统头文件

        Returns:
            dict: include信息数据结构
        """
        return {
            "file_name": file_name,
            "is_system": is_system,
        }

    # =========================
    # if宏相关静态方法
    # =========================
    @staticmethod
    def macro_if_info_init(
        context: UserFunctionContext,
        conditions: list,
        contents: list,
        else_content: Any = None,
    ) -> Any:
        """
        初始化C语言if宏信息数据字典。

        Args:
            context: 用户函数上下文
            conditions: 条件列表
            contents: 内容列表
            else_content: else内容

        Returns:
            dict: if宏信息数据结构
        """
        return {
            "conditions": conditions,
            "contents": contents,
            "else_content": else_content,
        }

    # =========================
    # 复合条件include相关静态方法
    # =========================
    @staticmethod
    def macro_conditional_include_info_init(
        context: UserFunctionContext,
        includes: list,
        include_condition: str = "",
        else_content: Any = None,
    ) -> Any:
        """
        复合C语言条件include信息数据字典。

        Args:
            context: 用户函数上下文
            includes: include文件列表
            include_condition: include条件
            else_content: else内容

        Returns:
            dict: 条件include数据结构
        """
        return CPlugin.macro_if_info_init(
            context=context,
            conditions=[include_condition] if include_condition else [],
            contents=[
                CPlugin.macro_include_info_init(context, inc) for inc in includes
            ],
            else_content=else_content,
        )

    # =========================
    # 注册所有用户函数
    # =========================
    @classmethod
    def functions(cls) -> List[UserFunctionInfo]:
        """
        返回所有可用的C语言模板用户函数信息。
        """
        return [
            UserFunctionInfo(
                name="c:macro_define_info_init",
                arg_range=(2, 2),
                description="生成C语言宏定义数据结构",
                handler=cls.macro_define_info_init,
            ),
            UserFunctionInfo(
                name="c:macro_include_info_init",
                arg_range=(1, 2),
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
        pass

    @classmethod
    def on_plugin_unload(cls):
        pass
