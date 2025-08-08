from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any, Union, Optional, Callable
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase, auto_register_factories


class Attr:
    """C语言属性信息"""

    @dataclass
    class Base(MetaBase):
        pass


class Expr:
    """C语言表达式体系的统一基类和命名空间"""

    @dataclass
    class Base(MetaBase):
        """C语言表达式的基类"""

        pass

    @dataclass
    class UnexposedMetaData(MetaBase):
        """C语言未暴露的表达式信息"""

        value: Any  # 表达式的原始值，可以是任意类型


class Decl:
    """C语言声明体系的统一基类和命名空间"""

    class Record:
        @dataclass
        class MetaData(MetaBase):
            """C语言结构体/联合体信息"""

            name: str  # 结构体/联合体名
            fields: List["Decl.Field.MetaData"] = field(default_factory=list)  # 字段列表
            attributes: List["Attr.Base"] = field(default_factory=list)  # 属性列表
            qualifiers: str = ""  # 结构体/联合体限定符，如const等

    class TypeRef:
        """C语言类型引用信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言类型引用信息"""

            ref: Union[
                str,  # 原生类型
                "Decl.Typedef.MetaData",  # typedef声明
                "Decl.Struct.MetaData",  # 结构体声明
                "Decl.Union.MetaData",  # 联合体声明
            ]

            def __str__(self):
                if isinstance(self.ref, str):
                    return self.ref
                elif isinstance(self.ref, Decl.Typedef.MetaData):
                    return self.ref.name
                elif isinstance(self.ref, Decl.Struct.MetaData):
                    return f"struct {self.ref.record.name}"
                elif isinstance(self.ref, Decl.Union.MetaData):
                    return f"union {self.ref.record.name}"
                else:
                    raise TypeError(f"Unsupported type reference: {type(self.ref)}")

    class TypeModifier:
        @dataclass
        class MetaData(MetaBase):
            """C语言类型修饰符信息"""

            type: "Decl.TypeRef.MetaData"  # 修饰的类型引用
            qualifiers: str = ""  # 类型限定符，如const/volatile
            attributes: List["Attr.Base"] = field(default_factory=list)  # 属性列表
            is_pointer: bool = False  # 是否为指针
            pointer_level: int = 0  # 指针层级，如int**为2
            is_array: bool = False  # 是否为数组
            array_dims: List[int] = field(default_factory=list)  # 支持多维数组，如[3,4]

    class Variable:
        @dataclass
        class MetaData(MetaBase):
            """C语言变量信息"""

            name: str  # 变量名
            modifier: "Decl.TypeModifier.MetaData"  # 变量类型修饰符
            init_expr: Optional["Expr.Base"] = None  # 初始化表达式，可能为None

    class Field:
        @dataclass
        class MetaData(MetaBase):
            """C语言结构/联合字段信息"""

            name: str  # 字段名（匿名字段可为空字符串）
            modifier: "Decl.TypeModifier.MetaData"  # 字段类型修饰符
            bitfield_width: Optional[int] = None  # 位域宽度，非位域为None

    class Typedef:
        """C语言类型定义声明信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言类型定义信息"""

            name: str
            typeref: "Decl.TypeRef.MetaData"

    class Struct:
        """C语言结构体声明信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言结构体信息"""

            record: "Decl.Record.MetaData"
            # fields: List["Decl.Field.MetaData"] = field(default_factory=list)

    class Union:
        """C语言联合声明信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言联合体信息"""

            record: "Decl.Record.MetaData"
            # fields: List["Decl.Field.MetaData"] = field(default_factory=list)

        @staticmethod
        def validator() -> Optional[UserFunctionValidator]:
            return None





class CPlugin(FunctionPlugin):

    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        info_funcs = auto_register_factories(Decl)[0]
        # 你还可以合并手写的其它函数
        return info_funcs

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
