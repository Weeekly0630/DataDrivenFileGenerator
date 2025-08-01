from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any


class TemplatePlugin(FunctionPlugin):
    """模板插件，用于处理模板相关的用户函数"""

    @staticmethod
    def string_join(context: UserFunctionContext, *args) -> str:
        """将字符串列表使用指定的分隔符连接成一个字符串"""
        connector = args[0]
        elements = args[1:]
        return connector.join(str(e) for e in elements)

    @staticmethod
    def string_join_validator() -> UserFunctionValidator:
        validator = UserFunctionValidator(validate_function_list=[])
        validator.add_param_check_validator(1, None)
        return validator

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        """返回插件提供的函数列表"""
        return [
            UserFunctionInfo(
                name="string_join",
                description="Join a list of strings with a specified connector",
                handler=cls.string_join,
                validator=cls.string_join_validator(),
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


# from modules.core import DataHandler
# from modules.core.user_function_resolver import UserFunctionInfo, UserFunctionContext, FunctionPlugin
# from modules.node.data_node import DataNode
# from typing import List, Callable, Any


# class StringPlugin(FunctionPlugin):
#     """字符串操作插件"""

#     @classmethod
#     def functions(cls) -> List[UserFunctionInfo]:

#         def join_string(
#             context: UserFunctionContext, *args
#         ) -> str:
#             s = args[0]
#             l = args[1:]
#             return str(s).join([str(e) for e in l])

#         return [
#             UserFunctionInfo(
#                 name="string:join",
#                 description="string:join(join_string: str, list: List): Join a list with string",
#                 handler=join_string,
#             ),
#         ]

#     @classmethod
#     def on_plugin_load(cls):
#         pass

#     @classmethod
#     def on_plugin_unload(cls):
#         pass
