from typing import Dict, Any, Callable, Protocol, List, Optional, Tuple
from dataclasses import dataclass
from ..node.expr_node import ExprASTParser, ExprPrintVistor
from .user_func.func_handler import UserFunctionResolver
from jinja2 import pass_context


# 定义过滤器 (只注册一次)
@pass_context
def expr_filter(ctx, *args: Tuple[Any, ...], **kwargs: Dict):
    """
    Jinja filter to process expressions.
    Args:
        *args: Positional arguments for the filte
        **kwargs: Keyword arguments for the filte
    Returns:
        str: Processed expression as a string.
    """
    # 从模板变量中获取值
    # 获取包含所有变量的字典
    # 获取完整的渲染数据字典
    # 递归向上查找
    resolver = ctx.resolve("__resolver__")
    node = ctx.resolve("__node__")

    print("===== 函数调试信息 =====")
    print(f"函数地址: {id(expr_filter):#x}")
    print(f"闭包捕获的解析器: {id(resolver):#x}")
    parser = ExprASTParser()
    node = parser.parse(args[0])
    return node.accept(ExprPrintVistor(resolver))


# def expr_filter_factory(resolver: UserFunctionResolver) -> Callable:
#     """ Expr Filter Factory for jinja2 filter register.
#     Args:
#         user_function_resolver: Dict[str, Callable]
#             Resolver dict for calling the user function in FunctionNode
#     Return: Callable
#     """
#     current_resolver = resolver
#     def expr_filter(*args: Tuple[Any, ...], **kwargs: Dict) -> str:
#         """
#         Jinja filter to process expressions.

#         Args:
#             *args: Positional arguments for the filter.
#             **kwargs: Keyword arguments for the filter.W

#         Returns:
#             str: Processed expression as a string.
#         """

#         parser = ExprASTParser()
#         node = parser.parse(args[0])
#         print("===== 函数调试信息 =====")
#         print(f"函数地址: {id(expr_filter):#x}")
#         print(f"闭包捕获的解析器: {id(current_resolver):#x}")
#         return node.accept(ExprPrintVistor(current_resolver))

#     return expr_filter
