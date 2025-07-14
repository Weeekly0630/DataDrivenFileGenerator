"""Core type definitions for the data driven generator"""

from enum import Enum

class DataHandlerType(Enum):
    """Enum for data handler types"""
    YAML_HANDLER = "yaml"  # 简化值以匹配配置文件

class TemplateHandlerType(Enum):
    """Enum for template handler types"""
    JINJA_HANDLER = "jinja"  # 简化值以匹配配置文件
