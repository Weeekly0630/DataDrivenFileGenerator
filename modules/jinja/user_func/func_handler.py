from typing import Dict, Any, Callable, Protocol, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from functools import wraps


class UserFunctionErrorType(Enum):
    """Error types for generator"""

    RESOLVER_INIT_ERROR = "resolver_init_error"
    FUNCTION_NOT_FOUND = "function_not_found"
    PARAMS_NUM_UNEXPECPED = "params_number_unexpected"
    PARAM_INVALID = ("param_invalid",)
    EXECUTION_FAILED = "execution_failed"


class UserFunctionError(Exception):
    """Base class for generator errors"""

    def __init__(self, error_type: UserFunctionErrorType, message: str) -> None:
        self.error_type = error_type
        self.message = message
        super().__init__(f"{error_type.value}: {message}")


@dataclass
class UserFunctionInfo:
    """用户定义函数信息"""

    name: str
    arg_range: tuple
    description: str
    handler: Callable


class UserFunctionResolver:
    """用户定义函数解析器"""

    def __init__(self, function_info: List[UserFunctionInfo]):
        self.info: Dict[str, UserFunctionInfo] = {}
        for info in function_info:
            if info.name in self.info:
                raise UserFunctionError(
                    UserFunctionErrorType.RESOLVER_INIT_ERROR,
                    message=f"Duplicate function found: {info.name}",
                )
            else:
                self.info[info.name] = info

    def add_function(self, function_info: UserFunctionInfo) -> bool:
        if function_info.name not in self.info:
            self.info[function_info.name] = function_info
            return True
        else:
            raise UserFunctionError(
                UserFunctionErrorType.RESOLVER_INIT_ERROR,
                message=f"Duplicate function found: {function_info.name}",
            )
            # return False

    def get_handler(self, func_name: str) -> Callable:
        """获取带验证的用户函数处理器

        Args:
            func_name: 用户函数名称

        Returns:
            Callable: 包装后的处理器函数

        Raises:
            UserFunctionError: 函数未找到或参数验证失败
        """
        # 1. 提前获取函数信息
        if func_name not in self.info:
            raise UserFunctionError(
                error_type=UserFunctionErrorType.FUNCTION_NOT_FOUND,
                message=f"Function {func_name} not found!",
            )

        info = self.info[func_name]
        handler = info.handler

        # 2. 使用闭包安全捕获当前值
        min_args, max_args = info.arg_range

        # 3. 使用装饰器模式避免重复定义
        @wraps(handler)  # 保留原函数元数据
        def wrapped_handler(*args: Tuple[Any, ...]) -> Any:
            """包装后的用户函数处理器"""
            argc = len(args)
            if argc < info.arg_range[0] or argc > info.arg_range[1]:
                raise UserFunctionError(
                    error_type=UserFunctionErrorType.PARAMS_NUM_UNEXPECPED,
                    message=f"Function expect [{info.arg_range[0]}~{info.arg_range[1]}] params but get {argc}",
                )

            # 参数类型/值验证
            # if not info.validate(*args):
            #     raise UserFunctionError(
            #         error_type=UserFunctionErrorType.PARAM_INVALID,
            #         message=f"Invalid parameter values for {func_name}",
            #     )

            try:
                # 执行实际处理函数
                return handler(*args)
            except Exception as e:
                # 捕获执行异常
                raise UserFunctionError(
                    error_type=UserFunctionErrorType.EXECUTION_FAILED,
                    message=f"Error executing {func_name}: {str(e)}",
                ) from e

        return wrapped_handler
