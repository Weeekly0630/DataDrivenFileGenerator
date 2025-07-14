"""
Expression Node Module
This module defines the `ExprNode` class, which represents an expression node in a tree structure.
"""

# from abc import ABC, abstractmethod

# from curses.ascii import SUB
from enum import Enum, auto
from typing import (
    Optional,
    List,
    Dict,
    Any,
    Type,
    TypeVar,
    Iterable,
    Union,
    Protocol,
    Callable,
)
from dataclasses import dataclass
from ..jinja.user_func.func_handler import UserFunctionResolver


class ExprNodeType(Enum):
    XPATH = auto()  # XPath表达式
    FUNCTION = auto()  # 函数调用
    EXPRESSION = auto()  # 复合表达式
    LITERAL = auto()  # 字面量常数
    # VARIABLE = auto()  # 变量


class ExprASTNode(Protocol):
    """抽象语法树节点基类"""

    source: Optional[Dict]

    def __init__(self, source: Optional[Dict] = None):
        # 保留原始字典数据用于调试和错误报告
        self.source: Optional[Dict] = source

    def accept(self, visitor: "ExprASTVisitor") -> Any:
        """访问者模式接受方法"""
        pass


class XPathNode(ExprASTNode):
    """XPath表达式节点"""

    def __init__(self, parts: List[ExprASTNode], source: Optional[Dict] = None):
        super().__init__(source)
        self.parts = parts  # 可以是字符串或嵌套节点

    def accept(self, visitor: "ExprASTVisitor") -> Any:
        return visitor.visit_xpath(self)


class FunctionNode(ExprASTNode):
    """函数调用节点"""

    def __init__(
        self, name: str, args: List[ExprASTNode], source: Optional[Dict] = None
    ):
        super().__init__(source)
        self.name = name
        self.args = args

    def accept(self, visitor: "ExprASTVisitor"):
        return visitor.visit_function(self)


class ExpressionOperator(Enum):
    """表达式操作符枚举"""

    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"
    AND = "&&"
    OR = "||"
    NOT = "!"
    EQ = "=="
    NEQ = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="


    def __str__(self):
        """返回操作符的字符串表示"""
        return self.name.lower()

class ExpressionNode(ExprASTNode):
    """表达式节点"""

    def __init__(
        self,
        operator: ExpressionOperator,
        operands: List[ExprASTNode],
        source: Optional[Dict] = None,
    ):
        super().__init__(source)
        self.operator = operator
        self.operands = operands

    def accept(self, visitor: "ExprASTVisitor"):
        return visitor.visit_expression(self)


class LiteralNode(ExprASTNode):
    """字面量节点（字符串、数字等）"""

    def __init__(
        self, value: Union[str, int, float, bool], source: Optional[Dict] = None
    ):
        super().__init__(source)
        self.value = value
        self.data_type: Type = self._infer_type(value)

    def _infer_type(self, value) -> Type:
        """推断字面量类型"""
        if isinstance(value, str):
            return str
        if isinstance(value, bool):
            return bool
        if isinstance(value, int):
            return int
        if isinstance(value, float):
            return float
        return str
        # return "unknown"

    def accept(self, visitor: "ExprASTVisitor"):
        return visitor.visit_literal(self)


class ExprASTParser:
    """将字典解析为ExprAST树"""

    def parse(self, data: Union[Dict, list, str, int, float, bool]) -> ExprASTNode:
        """
        解析入口点，处理各种输入类型
        """
        if isinstance(data, dict):
            return self._parse_dict(data)
        elif isinstance(data, list):
            raise ValueError("列表类型数据不支持直接解析为ExprAST节点")
            # return self._parse_list(data)
        else:
            return LiteralNode(data)

    def _parse_dict(self, data: Dict) -> ExprASTNode:
        """处理字典类型节点"""
        node_type = data.get("type")

        if node_type == "xpath":
            return self._parse_xpath(data)
        elif node_type == "function":
            return self._parse_function(data)
        elif node_type == "expression":
            return self._parse_expression(data)
        elif node_type == "literal":
            return self._parse_literal(data)
        else:
            raise ValueError(f"未知节点类型: {node_type}")

    def _parse_literal(self, data: Dict) -> LiteralNode:
        """解析字面量节点"""
        value = data.get("args", [None])[0]  # 默认取第一个参数作为值

        if value is None:
            raise ValueError("字面量节点缺少value字段")

        # 直接使用字面量值创建节点
        return LiteralNode(value, source=data)

    def _parse_xpath(self, data: Dict) -> XPathNode:
        """解析XPath节点"""
        args = data.get("args", [])
        parsed_parts = [self.parse(part) for part in args]
        return XPathNode(parsed_parts, source=data)

    def _parse_function(self, data: Dict) -> FunctionNode:
        """解析函数节点"""
        args = data.get("args", [])

        if not args:
            raise ValueError("函数节点必须至少有一个参数（函数名）")

        # 第一个参数是函数名
        func_name = args[0]

        # 解析函数参数
        parsed_args = [self.parse(arg) for arg in args[1:]]

        return FunctionNode(func_name, parsed_args, source=data)

    def _parse_expression(self, data: Dict) -> ExpressionNode:
        """解析表达式节点"""
        args = data.get("args", [])

        if not args:
            raise ValueError("表达式节点必须有操作符和操作数")

        # 第一个参数是操作符
        operator_str = args[0]
        # 剩余参数是操作数
        operands = args[1:]
        
        return ExpressionNode(
            operator=operator_str,
            operands=[self.parse(op) for op in operands],
            source=data,
        )


class ExprASTVisitor(Protocol):
    """访问者模式基类"""

    def visit_xpath(self, node: XPathNode):
        pass

    def visit_function(self, node: FunctionNode):
        pass

    def visit_expression(self, node: ExpressionNode):
        pass

    def visit_literal(self, node: LiteralNode):
        pass


class ExprPrintVistor(ExprASTVisitor):
    """打印ExprAST节点的访问者"""

    def __init__(self, user_function_resolver: UserFunctionResolver):
        self.resolver: UserFunctionResolver = user_function_resolver

    def visit_xpath(self, node: XPathNode) -> str:
        return "/".join(part.accept(self) for part in node.parts)

    def visit_function(self, node: FunctionNode) -> str:
        func_handler = self.resolver.get_handler(node.name)
        if func_handler:
            return func_handler(*[arg.accept(self) for arg in node.args])
        else:
            args_str = ", ".join(arg.accept(self) for arg in node.args)
            return f"{node.name}({args_str})"

    def visit_expression(self, node: ExpressionNode) -> str:
        return f"({str(node.operator).join(str(op.accept(self)) for op in node.operands)})"

    def visit_literal(self, node: LiteralNode) -> Union[str, int, float, bool]:
        # 根据类型决定是否添加引号
        return node.data_type(node.value)


# class ExprValidater(ExprASTVisitor):
#     """节点有效性检查器"""

#     def __init__(self):
#         self.errors = []

#     def visit_xpath(self, node: XPathNode) -> bool:
#         is_valid: bool = True
#         for part in node.parts:
#             if part.accept(self) is False:
#                 is_valid = False
#                 break
#         return is_valid

#     def visit_function(self, node: FunctionNode) -> bool:
#         # 这里可以添加特定函数的类型检查规则
#         for arg in node.args:
#             arg.accept(self)

#         # 示例：检查node:value函数参数数量
#         if node.name == "node:value" and len(node.args) != 1:
#             self.errors.append(f"函数 {node.name} 需要1个参数，但得到 {len(node.args)}")

#     def visit_expression(self, node: ExpressionNode):
#         # 检查操作数类型是否兼容
#         operand_types = [op.accept(self) for op in node.operands]

#         # 示例：检查比较运算符的操作数类型
#         if node.operator in ["=", "!=", "<", ">"]:
#             if len(operand_types) != 2:
#                 self.errors.append(f"比较运算符 '{node.operator}' 需要2个操作数")
#             elif operand_types[0] != operand_types[1]:
#                 self.errors.append(
#                     f"类型不匹配: {operand_types[0]} 和 {operand_types[1]}"
#                 )

#     def visit_literal(self, node: LiteralNode) -> str:
#         return node.data_type
