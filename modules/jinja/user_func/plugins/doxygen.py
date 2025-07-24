from modules.jinja.user_func.func_handler import UserFunctionInfo, UserFunctionContext
from modules.jinja.user_func.resolver import FunctionPlugin
from typing import List, Any

class DoxygenPlugin(FunctionPlugin):
    """DOXYGEN模板插件，提供Doxygen相关的Jinja用户函数"""

    # =========================
    # 文件头信息相关静态方法
    # =========================
    @staticmethod
    def file_info_init(
        context: UserFunctionContext,
        file: str,
        brief: str,
        version: str,
        group_name: str,
    ) -> Any:
        """
        初始化Doxygen文件头信息数据结构。

        Args:
            context: 用户函数上下文
            file: 文件名
            brief: 简要描述
            version: 版本号
            group_name: 分组名称

        Returns:
            dict: 文件头信息数据结构
        """
        return {
            "file": file,
            "brief": brief,
            "version": version,
            "group_name": group_name,
        }

    # =========================
    # 注册所有用户函数
    # =========================
    @classmethod
    def functions(cls) -> List[UserFunctionInfo]:
        """
        返回所有可用的DOXYGEN模板用户函数信息。
        """
        return [
            UserFunctionInfo(
                name="doxygen:file_info_init",
                arg_range=(4, 4),
                description="生成Doxygen文件头信息数据结构",
                handler=cls.file_info_init,
            ),
        ]

    @classmethod
    def on_plugin_load(cls):
        pass

    @classmethod
    def on_plugin_unload(cls):
        pass
