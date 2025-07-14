"""Command line interface for data-driven generator"""

import os
import sys
import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Union

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.core.data_driven_generator import DataDrivenGenerator, DataDrivenGeneratorConfig
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
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() == '.json':
                config = json.load(f)
            elif path.suffix.lower() in ['.yaml', '.yml']:
                config = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file type: {path.suffix}")
        
        # 处理相对路径
        config_dir = path.parent
        if 'data_config' in config:
            if 'root_path' in config['data_config']:
                root_path = Path(config['data_config']['root_path'])
                if not root_path.is_absolute():
                    config['data_config']['root_path'] = str(config_dir / root_path)
                    
        if 'template_config' in config:
            if 'template_dir' in config['template_config']:
                template_dir = Path(config['template_config']['template_dir'])
                if not template_dir.is_absolute():
                    config['template_config']['template_dir'] = str(config_dir / template_dir)
                    
        if 'output_dir' in config:
            output_dir = Path(config['output_dir'])
            if not output_dir.is_absolute():
                config['output_dir'] = str(config_dir / output_dir)
                
        return config
        
    except Exception as e:
        raise ValueError(f"Failed to parse config file: {str(e)}")

def save_output(output_dir: str, results: Dict[str, str]) -> None:
    """保存渲染结果到文件
    
    Args:
        output_dir: 输出目录
        results: 渲染结果字典，键为文件名，值为内容
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    for name, content in results.items():
        file_path = out_path / f"{name}.xml"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {file_path}")

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
    "patterns": ["root.yaml", "**/*.yaml"],
    "output_dir": "path/to/output"
}

配置文件格式示例 (YAML):
data_type: yaml
data_config:
    root_path: path/to/yaml/files
    file_pattern: ["*.yaml"]
template_type: jinja
template_config:
    template_dir: path/to/templates
patterns: ["root.yaml", "**/*.yaml"]
output_dir: path/to/output
""")
    
    parser.add_argument(
        'config',
        help='配置文件路径 (支持.json或.yaml/.yml)'
    )
    
    args = parser.parse_args()
    
    try:
        # 1. 加载配置
        config = load_config(args.config)
        
        # 2. 验证必要字段
        required_fields = [
            'data_type', 'data_config',
            'template_type', 'template_config',
            'patterns', 'output_dir'
        ]
        missing = [f for f in required_fields if f not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        
        # 3. 创建生成器配置
        gen_config = DataDrivenGeneratorConfig(
            data_type=DataHandlerType(config['data_type']),
            data_config=config['data_config'],
            template_type=TemplateHandlerType(config['template_type']),
            template_config=config['template_config']
        )
        
        # 4. 初始化生成器
        generator = DataDrivenGenerator(gen_config)
        print("\n==============Serialized File Tree==============")
        print(generator.data_handler.file_tree.serialize_tree())
        # 5. 处理每个模式
        for pattern in config['patterns']:
            print(f"\nProcessing pattern: {pattern}")
            results = generator.render(pattern)
            
            # 6. 保存结果
            save_output(config['output_dir'], results)
            
    except (ValueError, GeneratorError) as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()
