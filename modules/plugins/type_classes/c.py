from typing import List, Dict, Any, Union, Optional, Callable
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase


class Expression:
    """C语言表达式信息"""


class Preprocess:
    """C语言预处理信息"""

    class MacroDefinition:
        """C语言宏定义信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言宏定义的元数据"""

            name: str  # 宏名
            value: str  # 宏值（可通过 get_tokens 拼接）
            params: List[str] = field(default_factory=list)  # 宏参数（如有）
            comment: str = ""
            raw_code: str = ""

            def __str__(self):
                return f"#define {self.name}{'(' + ', '.join(self.params) + ')' if self.params else ''} {self.value}"
    class InclusionDirective:
        """C语言包含指令信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言包含指令信息"""

            filename: str  # 被包含的文件名
            is_system: bool = False  # 是否为系统头文件（<...>）

    class MacroInstantiation:
        """C语言宏实例化信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言宏实例化信息"""

            name: str  # 宏名
            args: List[str] = field(default_factory=list)  # 实例化参数（如有）

            def __str__(self):
                args_str = ", ".join(self.args) if self.args else ""
                return f"Macro Instantation: {self.name}{'(' + args_str + ')' if args_str else ''}"


class Attr:
    """C语言属性信息"""

    @dataclass
    class MetaData(MetaBase):
        args: List[str]


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
            fields: List["Decl.Field.MetaData"] = field(
                default_factory=list
            )  # 字段列表
            attribute: Optional[Attr.MetaData] = None
            qualifiers: str = ""  # 结构体/联合体限定符，如const等
            comment: str = ""  # 可选的注释信息

            # def __str__(self) -> str:
            #     return (
            #         f"{self.name} {{"
            #         + f"{', '.join(str(field) for field in self.fields)}}}"
            #         + (f" // {self.qualifiers}" if self.qualifiers else "")
            #     )

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

            # def __str__(self):
            #     if isinstance(self.ref, str):
            #         return self.ref
            #     elif isinstance(self.ref, Decl.Typedef.MetaData):
            #         return self.ref.name
            #     elif isinstance(self.ref, Decl.Struct.MetaData):
            #         return f"struct {self.ref.record.name}"
            #     elif isinstance(self.ref, Decl.Union.MetaData):
            #         return f"union {self.ref.record.name}"
            #     else:
            #         raise TypeError(f"Unsupported type reference: {type(self.ref)}")

    class TypeModifier:
        @dataclass
        class MetaData(MetaBase):
            """C语言类型修饰符信息"""

            type: "Decl.TypeRef.MetaData"  # 修饰的类型引用
            qualifiers: str  # 类型限定符，如const/volatile
            attribute: Optional[Attr.MetaData] = None  # 属性列表
            pointer_level: int = 0  # 指针层级，如int**为2
            array_dims: List[int] = field(default_factory=list)  # 支持多维数组，如[3,4]

            # def __str__(self):
            #     return f"{self.type}{'*' * self.pointer_level}{''.join(f'[{dim}]' for dim in self.array_dims)}{' ' + self.qualifiers if self.qualifiers else ''}"

    class Variable:
        @dataclass
        class MetaData(MetaBase):
            """C语言变量信息"""

            name: str  # 变量名
            storage_class: str  # 存储类修饰符，如static/extern等
            modifier: "Decl.TypeModifier.MetaData"  # 变量类型修饰符
            init_expr: str = ""  # 初始化表达式，可能为None
            comment: str = ""  # 可选的注释信息
            raw_code: str = ""  # 变量的原始代码文本

            # def __str__(self):
            #     parts = []
            #     if self.storage_class:
            #         parts.append(self.storage_class)
            #     parts.append(str(self.modifier.type))
            #     parts.append(self.name)
            #     if self.init_expr != "":
            #         parts.append(f"= {self.init_expr}")
            #     if self.comment:
            #         parts.append(f"// {self.comment}")
            #     return " ".join(parts)

    class Field:
        @dataclass
        class MetaData(MetaBase):
            """C语言结构/联合字段信息"""

            name: str  # 字段名（匿名字段可为空字符串）
            modifier: "Decl.TypeModifier.MetaData"  # 字段类型修饰符
            bitfield_width: Optional[int] = None  # 位域宽度，非位域为None
            raw_code: Optional[str] = None  # 变量的原始代码文本
            comment: Optional[str] = None  # 可选的注释信息

            # def __str__(self) -> str:
            #     return (
            #         f"{self.name}: {self.modifier.type}"
            #         + (f" : {self.bitfield_width}" if self.bitfield_width else "")
            #         + (f" // {self.comment}" if self.comment else "")
            #     )

    class Typedef:
        """C语言类型定义声明信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言类型定义信息"""

            name: str
            typeref: "Decl.TypeRef.MetaData"
            comment: str = ""
            raw_code: Optional[str] = None  # 变量的原始代码文本

            # def __str__(self) -> str:
            #     return f"typedef {self.typeref} {self.name}"

    class Struct:
        """C语言结构体声明信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言结构体信息"""

            record: "Decl.Record.MetaData"
            raw_code: str = ""  # 变量的原始代码文本

            # fields: List["Decl.Field.MetaData"] = field(default_factory=list)

    class Union:
        """C语言联合声明信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言联合体信息"""

            record: "Decl.Record.MetaData"
            raw_code: Optional[str] = None  # 变量的原始代码文本

            # def __str__(self) -> str:
            #     return str(
            #         f"union {self.record}"
            #     )

    class Param:
        """C语言函数参数信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言函数参数信息"""

            name: str  # 参数名
            modifier: "Decl.TypeModifier.MetaData"  # 参数类型修饰符
            raw_code: Optional[str] = None  # 参数的原始代码文本

            # def __str__(self) -> str:
            #     return f"{self.modifier.type} {self.name}"

    class Function:
        """C语言函数声明信息"""

        @dataclass
        class MetaData(MetaBase):
            """C语言函数信息"""

            name: str  # 函数名
            return_type: "Decl.TypeRef.MetaData"
            params: List["Decl.Param.MetaData"] = field(
                default_factory=list
            )  # 参数列表
            comment: str = ""
            raw_code: str = ""  # 函数的原始代码文本

            # def __str__(self):
            #     params_str = ", ".join([str(param) for param in self.params])
            #     comment_str = f" // {self.comment}" if self.comment else ""
            #     return f"{self.return_type} {self.name}({params_str}) {comment_str}"
    class EnumConstant:
        @dataclass
        class MetaData(MetaBase):
            """C语言枚举常量信息"""

            name: str
            value: int
            comment: str
            raw_code: str

    class Enum:
        @dataclass
        class MetaData(MetaBase):
            """C语言枚举信息"""

            name: str
            constants: List["Decl.EnumConstant.MetaData"]
            comment: str
            raw_code: str