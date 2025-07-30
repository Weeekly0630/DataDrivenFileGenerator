"""Data-driven generator module for Jinja Template"""

from typing import Dict, Any, List, Tuple, Union
from dataclasses import dataclass
from . import (
    GeneratorError,
    GeneratorErrorType,
    DataHandler,
    TemplateHandler,
    validate_data_context,
    validate_render_result,
)
from .handler_factory import HandlerFactory
from .types import DataHandlerType, TemplateHandlerType
from ..node.data_node import DataNode
from ..jinja.user_func.func_handler import UserFunctionInfo, UserFunctionResolver


@dataclass
class DataDrivenGeneratorConfig:
    """Configuration for the DataDrivenGenerator"""

    data_type: DataHandlerType  # 数据处理器类型
    data_config: Dict[str, Any]  # 数据处理器配置
    template_type: TemplateHandlerType  # 模板处理器类型
    template_config: Dict[str, Any]  # 模板处理器配置

    preserved_template_key: str  # 指定字典树中的字典的保留模板键
    preserved_children_key: str  # 指定字典树中的字典的保留子节点键
    preserved_children_content_key: str  # 指定模板中引用子节点数据对象名称


class FlexibleChildrenContent:
    """Auto handle Cildren Content"""

    def __init__(self, children_content: Union[str, List]) -> None:
        self.children_content = children_content

    def __str__(self) -> str:
        """Convert to string representation"""
        if isinstance(self.children_content, list):
            return "\n".join(str(item) for item in self.children_content)
        return str(self.children_content)

    def __item__(self, item: Union[str, int]) -> str:
        """Get item by index or key"""
        if isinstance(self.children_content, list):
            return self.children_content[item]
        elif isinstance(self.children_content, dict):
            return self.children_content.get(item, "")
        else:
            return str(self.children_content)
        raise TypeError("Children content must be a list or dict")

class DataDrivenGenerator:
    """Data-driven generator class
    This class is responsible for generating data-driven templates based on provided data.
    """

    def __init__(
        self,
        config: DataDrivenGeneratorConfig,
    ) -> None:
        """Initialize the generator with configuration

        Args:
            config: Configuration for data and template handlers
        """
        self.data_handler = HandlerFactory.create_data_handler(
            config.data_type, config.data_config
        )
        self.template_handler = HandlerFactory.create_template_handler(
            config.template_type, config.template_config
        )
        self.config = config

    def _rendered_contents_init(self) -> None:
        # 存储渲染结果的映射
        self._rendered_contents: Dict[DataNode, str] = {}

    def render_by_pattern(self, pattern: str) -> Dict[str, str]:
        """Render templates based on the provided pattern

        Args:
            pattern: Pattern to match data files

        Returns:
            Dict[str, str]: Rendered template contents keyed by node name

        Raises:
            GeneratorError: If rendering fails or no templates are found
        """
        result: Dict[str, str] = {}

        # Prepare param dict
        if self.config.data_type == DataHandlerType.YAML_HANDLER:
            kvargs = {
                "pattern": pattern,
                "preserved_children_key": self.config.preserved_children_key,
            }

        # 1. 创建数据树
        roots = self.data_handler.create_data_tree(**kvargs)
        if len(roots) == 0:
            raise GeneratorError(
                GeneratorErrorType.DATA_INIT_ERROR,
                f"No data files found matching pattern: {pattern}",
            )
        # 1.1 打印数据树
        print("\n==============Serialized Data Tree==============")

        # 2. 遍历数据树进行渲染
        for root in roots:
            if not isinstance(root, DataNode):
                raise TypeError("Root must be an instance of DataNode")
            # 2.1 打印数据树
            print(root.serialze())

            # 2.2 后续遍历
            self._process_node(root)

            # 2.3 取结果
            result[root._parent.meta_data.name] = self._rendered_contents.get(root, "")

        return result

    def render(self, *args, **kvargs) -> dict:
        """渲染模板，支持多种渲染参数"""
        # 清空之前的渲染结果
        self._rendered_contents_init()
        # 支持 pattern 参数对象
        if "pattern" in kvargs:
            pattern = kvargs["pattern"]
            # 支持 pattern 为字符串或列表
            patterns = [pattern] if isinstance(pattern, str) else pattern
            results = {}
            for pat in patterns:
                result = self.render_by_pattern(pat)
                results.update(result)
            # 返回所有渲染结果
            return results
        else:
            raise ValueError("Please use pattern in config dict.")

    def _process_node(self, root: DataNode) -> None:
        """处理单个节点及其子节点

        采用后序遍历（先处理子节点再处理父节点）

        Args:
            node: 要处理的数据节点
        """

        def children_content_init(node: DataNode, preserved_key: str) -> None:
            """Initialize children content key in the node data"""
            if preserved_key not in node.data:
                node.data[preserved_key] = []

        def children_content_update(
            node: DataNode,
            preserved_key: str,
            rendered_content_map: Dict[DataNode, str],
        ) -> None:
            """Update children content key in the node data with rendered contents
            DataNode.parent.parent.children = Any ==> DataNode.data[preserved_key]
            """

            def extract_content(children):
                if children is None:
                    return ""
                elif isinstance(children, list):
                    # Recursively process each element
                    return [extract_content(child) for child in children]
                else:
                    # children is a DataNode wrapper (e.g., FileNode or DataNode itself)
                    obj = getattr(children, "mapping_obj", None)
                    if isinstance(obj, DataNode):
                        return rendered_content_map.get(obj, "")
                    return ""

            node.data[preserved_key] = extract_content(node._parent._parent.children)

        def visitor(node: DataNode, *args) -> None:
            """Visitor function to process each node"""
            if not isinstance(node, DataNode):
                raise TypeError("Node must be an instance of DataNode")
            # 校验DataNode数据
            validate_data_context(node.data, self.config.preserved_children_key)
            validate_data_context(node.data, self.config.preserved_template_key)
            # 打印当前节点信息
            print(f"Processing node: {node._parent.meta_data.name}")
            # 初始化children_content
            children_content_init(node, self.config.preserved_children_content_key)
            # 更新children_content
            children_content_update(
                node,
                self.config.preserved_children_content_key,
                self._rendered_contents,
            )
            # 预处理复合表达式

            # 进行渲染
            try:
                template_path = node.data[self.config.preserved_template_key]
                # 渲染模板
                result = self.template_handler.render(template_path, node.data)
                # 验证渲染结果并保存
                validate_render_result(result, template_path)
                self._rendered_contents[node] = result
            except Exception as e:
                raise GeneratorError(
                    GeneratorErrorType.RENDER_ERROR,
                    f"Failed to render {template_path}: {str(e)}",
                )

        # 进行后序遍历
        root.post_traverse(visitor)
