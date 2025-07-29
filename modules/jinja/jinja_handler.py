from jinja2 import (
    Environment,
    FileSystemLoader,
    Template,
    pass_context,
    StrictUndefined,
)
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from pathlib import Path

from .expr_filter import expr_filter
from modules.node.data_node import DataNode
from modules.core import DataHandler
from ..core import TemplateHandler

@dataclass
class JinjaConfig:
    """Jinja模板配置"""

    template_dir: Path  # 模板目录路径
    encoding: str  # 文件编码
    autoescape: bool  # XML转义开关

    @classmethod
    def validate(cls, config: Dict[str, Any]) -> "JinjaConfig":
        """验证配置并返回配置对象

        Args:
            config: 配置字典，必须包含template_dir

        Returns:
            JinjaConfig: 配置对象

        Raises:
            ValueError: 如果配置无效
        """
        if "template_dir" not in config:
            raise ValueError("Missing required field 'template_dir'")

        template_dir = Path(config["template_dir"])
        if not template_dir.exists():
            raise ValueError(f"template_dir {template_dir} does not exist")

        return cls(
            template_dir=template_dir,
            encoding=config.get("encoding", "utf-8"),
            autoescape=config.get("autoescape", False),
        )


class JinjaTemplateHandler(TemplateHandler):
    """Jinja模板处理器"""

    def __init__(self, config: Dict[str, Any]) -> None:
        """初始化Jinja环境

        Args:
            config: 配置字典，必须包含template_dir

        Raises:
            ValueError: 如果配置无效
        """
        self.config = JinjaConfig.validate(config)

        # 创建Jinja环境
        self.env = Environment(
            loader=FileSystemLoader(
                str(self.config.template_dir), encoding=self.config.encoding
            ),
            autoescape=self.config.autoescape,
            trim_blocks=True,  # 移除块级标签后的第一个换行
            lstrip_blocks=True,  # 移除块级标签前的空白
            keep_trailing_newline=True,  # 保留文件末尾的换行
            undefined=StrictUndefined,  # 严格模式，未定义变量会抛出错误
        )

    # def register_filter(self, name: str, func: Callable) -> None:
    #     """注册自定义过滤器

    #     Args:
    #         name: 过滤器名称
    #         func: 过滤器函数
    #     """
    #     self.env.filters[name] = func

    def render(
        self, template_path: str, data: Dict
    ) -> str:
        """渲染模板

        Args:
            template_path: 模板文件路径（相对于template_dir）
            data: 渲染上下文数据
            resolver: 可选的解析器字典，用于注册额外的过滤器

        Returns:
            str: 渲染结果

        Raises:
            jinja2.TemplateNotFound: 如果模板不存在
            jinja2.TemplateError: 如果渲染过程出错
        """
        template = self.env.get_template(template_path)
        return template.render(data)
