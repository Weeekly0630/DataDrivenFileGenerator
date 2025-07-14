from typing import Dict, Any, Callable, Protocol, List, Optional, Tuple
from dataclasses import dataclass
from ..node.expr_node import ExprASTParser, ExprPrintVistor
from .user_func.func_handler import UserFunctionResolver


def expr_filter_factory(resolver: UserFunctionResolver) -> Callable:
    """ Expr Filter Factory for jinja2 filter register.
    Args:
        user_function_resolver: Dict[str, Callable] 
            Resolver dict for calling the user function in FunctionNode
    Return: Callable
        
    """
    def expr_filter(*args: Tuple[Any, ...], **kwargs: Dict) -> str:
        """
        Jinja filter to process expressions.

        Args:
            *args: Positional arguments for the filter.
            **kwargs: Keyword arguments for the filter.

        Returns:
            str: Processed expression as a string.
        """

        parser = ExprASTParser()
        node = parser.parse(args[0])
        return node.accept(ExprPrintVistor(resolver))

    return expr_filter
