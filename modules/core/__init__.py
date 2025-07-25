"""Core module for data driven generator"""

from enum import Enum
from typing import (
    Protocol,
    Dict,
    Any,
    List,
    Optional,
    Iterator,
    runtime_checkable,
    Callable,
    Type,
)
from pathlib import Path
from ..node.data_node import DataNode
from modules.node.file_node import DirectoryNode


@runtime_checkable
class DataHandler(Protocol):
    """Protocol for data handlers
    一个DataHander需要做到:
        - 初始化时接收配置
        - 创建数据字典树
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the data handler with configuration

        Args:
            config: Configuration for the data handler
        """
        ...

    def create_data_tree(self, *args, **kvargs) -> DataNode:
        """根据输入参数，创建数据字典树, 具体读取数据的方式由具体的处理器决定"""
        ...


@runtime_checkable
class TemplateHandler(Protocol):
    """Protocol for template handlers
    一个TemplateHandler需要做到:
        - 初始化时接收配置
        - 指定模板并渲染
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the template handler with configuration

        Args:
            config: Configuration for the template handler
        """
        ...

    def render(self, template_path: str) -> str:
        """Render the template with the given path"""
        ...


class GeneratorErrorType(Enum):
    """Error types for generator"""

    DATA_INIT_ERROR = "data_init_error"
    TEMPLATE_INIT_ERROR = "template_init_error"
    RENDER_ERROR = "render_error"
    TEMPLATE_NOT_FOUND = "template_not_found"


class GeneratorError(Exception):
    """Base class for generator errors"""

    def __init__(self, error_type: GeneratorErrorType, message: str) -> None:
        self.error_type = error_type
        self.message = message
        super().__init__(f"{error_type.value}: {message}")


def validate_data_handler(handler: Any) -> None:
    """验证数据处理器是否实现了所有必要的方法

    Args:
        handler: 要验证的处理器实例

    Raises:
        GeneratorError: 如果处理器没有实现所有必要的方法
    """
    if not isinstance(handler, DataHandler):
        raise GeneratorError(
            GeneratorErrorType.DATA_INIT_ERROR,
            "Data handler must implement DataHandler protocol",
        )


def validate_template_handler(handler: Any) -> None:
    """验证模板处理器是否实现了所有必要的方法"""
    if not isinstance(handler, TemplateHandler):
        raise GeneratorError(
            GeneratorErrorType.TEMPLATE_INIT_ERROR,
            "Template handler must implement TemplateHandler protocol",
        )


def validate_data_context(data: Dict[str, Any], template_key: str) -> None:
    """验证数据上下文是否包含必要的键"""
    if template_key not in data:
        raise GeneratorError(
            GeneratorErrorType.TEMPLATE_NOT_FOUND,
            f"Missing required key '{template_key}' in data",
        )


def validate_render_result(result: Optional[str], template_path: str) -> None:
    """验证渲染结果是否有效"""
    if result is None:
        raise GeneratorError(
            GeneratorErrorType.RENDER_ERROR,
            f"Failed to render template: {template_path}",
        )
