from typing import Dict, Any, Callable, Protocol, List, Optional, Tuple
from dataclasses import dataclass
from ..node.expr_node import ExprASTParser, ExprPrintVistor
from .user_func.func_handler import UserFunctionResolver
from jinja2 import pass_context


# 定义过滤器 (只注册一次)
def expr_filter(*args, **kwargs: Dict):
    """
    Jinja filter to process expressions.
    Args:
        *args: Positional arguments for the filte
        **kwargs: Keyword arguments for the filte
    Returns:
        str: Processed expression as a string.
    """
    if isinstance(args[1], Dict):
        resolver = args[1].get("resolver", None)
        if not isinstance(resolver, UserFunctionResolver):
            raise ValueError(
                "The 'resolver' key must be a UserFunctionResolver instance."
            )
    else:
        raise ValueError(
            "The second argument must be a dictionary containing 'resolver' key."
        )

    # print("===== 函数调试信息 =====")
    # print(f"闭包捕获的解析器: {id(resolver):#x}")
    parser = ExprASTParser()
    expr_node = parser.parse(args[0])
    return expr_node.accept(ExprPrintVistor(resolver))