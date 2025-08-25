from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any, Union, Optional, Callable
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase, auto_register_factories
from modules.plugins.type_classes.c import Decl
from modules.utils.clang.extractor import (
    CursorExtractVisitor,
    ClangExtractor,
    ClangExtractorOptional,
)


class CPlugin(FunctionPlugin):

    @staticmethod
    def extract_decl_from_c(
        context: UserFunctionContext,
        lib_clang_path: str,
        file_path: str,
        c_args: List[str] = [],
        debug_level: int = 0,
        main_file_only: bool = False,
    ) -> "CursorExtractVisitor":
        """提取C语言文件的声明信息，返回一个CursorExtractVisitor实例"""
        extractor = ClangExtractor(lib_clang_path)
        visitor = extractor.extract(
            file_path,
            ClangExtractorOptional(
                c_args=c_args, debug_level=debug_level, main_file_only=main_file_only
            ),
        )
        return visitor

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        info_funcs = auto_register_factories(Decl)[0]
        # 你还可以合并手写的其它函数
        user_function_infos = [
            UserFunctionInfo(
                name="extract_decl_from_c",
                description="提取C语言文件的声明信息，返回一个CursorExtractVisitor实例",
                handler=cls.extract_decl_from_c,
            )
        ]
        infos = user_function_infos + info_funcs
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
