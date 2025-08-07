"""Command line interface for data-driven generator"""

import os
import sys
import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Union

# 获取当前文件所在目录（modules目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（xdm_template目录）
project_root = os.path.dirname(current_dir)
# 获取顶级包目录（code目录）
code_dir = os.path.dirname(project_root)

# 将顶级包目录添加到Python路径
sys.path.insert(0, code_dir)

from modules.core.data_driven_generator import (
    DataDrivenGenerator,
    DataDrivenGeneratorConfig,
)
from modules.core.types import DataHandlerType, TemplateHandlerType
from modules.core import GeneratorError


def load_config(file_path: str) -> Dict[str, Any]:
    """加载配置文件并处理路径

    支持JSON和YAML格式的配置文件，自动处理相对路径

    Args:
        file_path: 配置文件路径

    Returns:
        Dict[str, Any]: 配置内容

    Raises:
        ValueError: 如果文件格式不支持或解析失败
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise ValueError(f"Config file not found: {file_path}")

    try:
        # 加载配置
        with open(path, "r", encoding="utf-8") as f:
            if path.suffix.lower() == ".json":
                config = json.load(f)
            elif path.suffix.lower() in [".yaml", ".yml"]:
                config = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file type: {path.suffix}")

        # 处理相对路径
        config_dir = path.parent
        # 字段映射：将 root_path 映射为 file_root_path，兼容旧配置
        if "data_config" in config:
            data_cfg = config["data_config"]
            # 字段映射
            if "root_path" in data_cfg and "file_root_path" not in data_cfg:
                data_cfg["file_root_path"] = data_cfg.pop("root_path")
            # 处理相对路径
            if "file_root_path" in data_cfg:
                root_path = Path(data_cfg["file_root_path"])
                if not root_path.is_absolute():
                    data_cfg["file_root_path"] = str(config_dir / root_path)

        if "template_config" in config:
            if "template_dir" in config["template_config"]:
                template_dir = Path(config["template_config"]["template_dir"])
                if not template_dir.is_absolute():
                    config["template_config"]["template_dir"] = str(
                        config_dir / template_dir
                    )

        if "output_dir" in config:
            output_dir = Path(config["output_dir"])
            if not output_dir.is_absolute():
                config["output_dir"] = str(config_dir / output_dir)

        return config

    except Exception as e:
        raise ValueError(f"Failed to parse config file: {str(e)}")


def save_output(output_dir: str, results: dict, file_extension: str) -> None:
    """保存渲染结果到文件

    Args:
        output_dir: 输出目录
        results: 渲染结果字典，键为文件名，值为内容
    """

    def name_extension(file_path: str, extension: str) -> str:
        """
        移除文件路径的一个后缀名，并添加指定的扩展名

        参数:
            file_path: 原始文件路径
            extension: 要添加的新扩展名（带或不带点均可，空字符串表示只移除不添加）

        返回:
            处理后的新文件路径
        """

        # 分离目录路径和文件名
        dir_name, file_name = os.path.split(file_path)

        # 处理文件名部分
        if "." in file_name:
            # 只移除一个后缀名（最后一个点之后的部分）
            base_name = file_name.rsplit(".", 1)[0]
        else:
            # 没有后缀名则保持原样
            base_name = file_name

        # 处理扩展名
        if extension:
            # 确保扩展名以点开头
            if not extension.startswith("."):
                extension = "." + extension
            new_filename = base_name + extension
        else:
            # 扩展名为空字符串，保持原文件名
            new_filename = base_name

        # 重新组合完整路径
        return os.path.join(dir_name, new_filename)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    for name, content in results.items():
        file_path = out_path / name_extension(name, file_extension)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {file_path}\n")


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(
        description="Data-driven generator command line tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
配置文件格式示例 (JSON):
{
    "data_type": "yaml",
    "data_config": {
        "root_path": "path/to/yaml/files",
        "file_pattern": ["*.yaml"]
    },
    "template_type": "jinja",
    "template_config": {
        "template_dir": "path/to/templates"
    },
    "pattern": ["root.yaml", "**/*.yaml"],
    "output_dir": "path/to/output",
    "preserved_template_key": "TEMPLATE",
    "preserved_children_key": "CHILDREN",
    "preserved_children_content_key": "CHILDREN_CONTENT"
}

配置文件格式示例 (YAML):
data_type: yaml
data_config:
    root_path: path/to/yaml/files
    file_pattern: ["*.yaml"]
template_type: jinja
template_config:
    template_dir: path/to/templates
pattern: ["root.yaml", "**/*.yaml"]
output_dir: path/to/output
preserved_template_key: TEMPLATE
preserved_children_key: CHILDREN
preserved_children_content_key: CHILDREN_CONTENT
""",
    )

    parser.add_argument("config", help="配置文件路径 (支持.json或.yaml/.yml)")

    args = parser.parse_args()

    try:
        # 1. 加载配置
        config = load_config(args.config)

        # 2. 验证必要字段
        required_fields = [
            "data_type",
            "data_config",
            "template_type",
            "template_config",
            "pattern",
            "output_dir",
            "preserved_template_key",
            "preserved_children_key",
            "preserved_children_content_key",
        ]
        missing = [f for f in required_fields if f not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        # 3. 创建生成器配置
        gen_config = DataDrivenGeneratorConfig(
            data_type=DataHandlerType(config["data_type"]),
            data_config=config["data_config"],
            template_type=TemplateHandlerType(config["template_type"]),
            template_config=config["template_config"],
            preserved_template_key=config.get("preserved_template_key", "TEMPLATE"),
            preserved_children_key=config.get("preserved_children_key", "CHILDREN"),
            preserved_children_content_key=config.get(
                "preserved_children_content_key", "CHILDREN_CONTENT"
            ),
        )

        # 4. 初始化生成器
        generator = DataDrivenGenerator(gen_config)

        # 5. 处理
        render_param = {}
        if "pattern" in config:
            render_param["pattern"] = config["pattern"]
        # 未来可扩展更多参数
        print(f"\nProcessing render params: {render_param}")
        results = generator.render(**render_param)

        # 6. 保存结果
        save_output(
            config["output_dir"],
            results,
            file_extension=config.get("output_file_extension", ""),
        )

    except (ValueError, GeneratorError) as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
