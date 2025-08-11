from modules.core.user_function_resolver import (
    UserFunctionContext,
    UserFunctionInfo,
    FunctionPlugin,
    UserFunctionValidator,
)
from typing import List, Dict, Any, Union, Optional, Callable
from dataclasses import dataclass, field, asdict
from modules.plugins.type import MetaBase, auto_register_factories, FunctionRegistry
from modules.node.data_node import DataNode
import os
import re
import glob
from pathlib import Path

class JinjaMacroCollectorPlugin(FunctionPlugin):
    """Jinja2宏收集插件，用于扫描和收集模板文件中的宏定义"""
    
    @staticmethod
    def collect_jinja_macros(template_dir: str, pattern: str = "**/*.j2") -> List[Dict[str, Any]]:
        """
        收集指定目录下所有Jinja2模板文件中的宏定义
        
        Args:
            template_dir: 模板目录路径
            pattern: 文件匹配模式，默认为 "**/*.j2"
            
        Returns:
            List[Dict]: 宏信息列表，每个字典包含宏的详细信息
        """
        macros = []
        template_path = Path(template_dir).resolve()
        
        if not template_path.exists():
            print(f"模板目录不存在: {template_dir}")
            return macros
        
        # 使用glob查找所有匹配的模板文件
        search_pattern = str(template_path / pattern)
        template_files = glob.glob(search_pattern, recursive=True)
        
        print(f"扫描模板目录: {template_dir}")
        print(f"匹配模式: {pattern}")
        print(f"找到 {len(template_files)} 个模板文件")
        
        for file_path in template_files:
            try:
                file_macros = JinjaMacroCollectorPlugin._parse_jinja_file(file_path, template_dir)
                macros.extend(file_macros)
                if file_macros:
                    print(f"  {file_path}: 发现 {len(file_macros)} 个宏")
            except Exception as e:
                print(f"  解析文件失败 {file_path}: {e}")
                continue
        
        print(f"总共收集到 {len(macros)} 个宏定义")
        return macros
    
    @staticmethod
    def _parse_jinja_file(file_path: str, base_dir: str) -> List[Dict[str, Any]]:
        """
        解析单个Jinja2文件，提取其中的宏定义
        
        Args:
            file_path: 文件路径
            base_dir: 基础目录，用于计算相对路径
            
        Returns:
            List[Dict]: 该文件中的宏信息列表
        """
        macros = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return macros
        
        # 计算相对路径
        rel_path = os.path.relpath(file_path, base_dir).replace('\\', '/')
        
        # 正则表达式匹配宏定义
        # 匹配: {% macro macro_name(param1, param2, ...) %}
        macro_pattern = r'\{%\s*-?\s*macro\s+(\w+)\s*\((.*?)\)\s*-?\s*%\}'
        
        matches = re.finditer(macro_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            macro_name = match.group(1).strip()
            params_str = match.group(2).strip()
            
            # 解析参数列表
            params = []
            if params_str:
                # 简单的参数解析，按逗号分割并清理空白
                param_list = [p.strip() for p in params_str.split(',')]
                params = [p for p in param_list if p]  # 移除空字符串
            
            # 尝试提取宏的注释描述（查找宏定义前的注释）
            description = JinjaMacroCollectorPlugin._extract_macro_description(content, match.start())
            
            macro_info = {
                'name': macro_name,
                'args': params,
                'template_path': rel_path,
                'description': description,
                'file_path': file_path,  # 完整文件路径，便于调试
            }
            
            macros.append(macro_info)
        
        return macros
    
    @staticmethod
    def _extract_macro_description(content: str, macro_start: int) -> str:
        """
        尝试提取宏定义前的注释作为描述
        
        Args:
            content: 文件内容
            macro_start: 宏定义开始位置
            
        Returns:
            str: 宏的描述信息
        """
        # 查找宏定义前的内容
        before_macro = content[:macro_start]
        lines = before_macro.split('\n')
        
        # 从后往前查找注释行
        description_lines = []
        for line in reversed(lines[-10:]):  # 只检查前10行
            line = line.strip()
            if line.startswith('{#') and line.endswith('#}'):
                # Jinja2注释格式: {# 注释内容 #}
                comment = line[2:-2].strip()
                description_lines.insert(0, comment)
            elif line.startswith('<!--') and line.endswith('-->'):
                # HTML注释格式: <!-- 注释内容 -->
                comment = line[4:-3].strip()
                description_lines.insert(0, comment)
            elif line == '' or line.startswith('{%') or line.startswith('{{'):
                # 遇到空行或其他Jinja语法，停止查找
                break
            else:
                # 其他非注释行，停止查找
                break
        
        return ' '.join(description_lines) if description_lines else ""
    
    @staticmethod
    def create_macro_collector(context: UserFunctionContext, template_dir: str, pattern: str = "**/*.j2", path_prefix: str = "") -> Dict[str, Any]:
        """
        创建宏收集器，收集指定目录下的所有Jinja2宏，返回与defines.j2模板兼容的数据格式
        
        Args:
            context: 用户函数上下文
            template_dir: 模板目录路径
            pattern: 文件匹配模式
            path_prefix: 模板路径前缀，用于生成完整的import路径
            
        Returns:
            Dict: 包含 infos 列表的字典，直接兼容 defines.j2 模板
        """
        macros = JinjaMacroCollectorPlugin.collect_jinja_macros(template_dir, pattern)
        
        # 转换为 defines.j2 需要的格式
        infos = []
        
        for macro in macros:
            # 生成模块名（从文件路径推导）
            # 例如: "C/decl/struct.j2" -> "Struct"
            path_parts = macro['template_path'].replace('.j2', '').split('/')
            module_name = path_parts[-1].title()  # 取最后一部分并首字母大写
            
            # 确保模块名是有效的标识符
            module_name = ''.join(c for c in module_name if c.isalnum() or c == '_')
            if not module_name[0].isalpha():
                module_name = 'M' + module_name
            
            # 处理路径前缀
            full_module_path = macro['template_path']
            if path_prefix:
                # 确保前缀以 / 结尾
                normalized_prefix = path_prefix.rstrip('/') + '/'
                full_module_path = normalized_prefix + macro['template_path']
            
            info = {
                'module_path': full_module_path,        # 带前缀的完整模板路径
                'module_name': module_name,             # 导入别名
                'macro_name': macro['name'],            # 宏名称
                'description': macro['description'],     # 描述（额外信息）
                'args': macro['args'],                  # 参数列表（额外信息）
                'original_path': macro['template_path'] # 原始相对路径（备用）
            }
            
            infos.append(info)
        
        # 按模板文件分组（保留原有信息）
        grouped_by_file = {}
        for macro in macros:
            file_path = macro['template_path']
            if file_path not in grouped_by_file:
                grouped_by_file[file_path] = []
            grouped_by_file[file_path].append(macro)
        
        # 统计信息
        total_files = len(grouped_by_file)
        total_macros = len(macros)
        
        result = {
            'infos': infos,  # defines.j2 需要的主要数据
            'macros': macros,  # 原始宏信息（备用）
            'grouped_by_file': grouped_by_file,  # 按文件分组（备用）
            'statistics': {
                'total_files': total_files,
                'total_macros': total_macros,
                'template_dir': template_dir,
                'pattern': pattern,
                'path_prefix': path_prefix
            }
        }
        
        return result
    
    @classmethod
    def functions(cls) -> List["UserFunctionInfo"]:
        """
        注册宏收集相关的用户函数
        """
        
        def collect_macros_handler(context: UserFunctionContext, template_dir: str, pattern: str = "**/*.j2", path_prefix: str = "") -> Dict[str, Any]:
            """宏收集处理器 - 返回结构化数据"""
            return cls.create_macro_collector(context, template_dir, pattern, path_prefix)
        
        def collect_macros_for_defines_handler(context: UserFunctionContext, template_dir: str, pattern: str = "**/*.j2", path_prefix: str = "") -> List[Dict[str, Any]]:
            """宏收集处理器 - 专为 defines.j2 模板返回 infos 列表"""
            result = cls.create_macro_collector(context, template_dir, pattern, path_prefix)
            return result['infos']
        
        def collect_macros_summary_handler(context: UserFunctionContext, template_dir: str, pattern: str = "**/*.j2", path_prefix: str = "") -> str:
            """宏收集摘要处理器 - 返回文本摘要"""
            result = cls.create_macro_collector(context, template_dir, pattern, path_prefix)
            
            summary = f"Jinja2宏收集完成:\n"
            summary += f"- 扫描目录: {result['statistics']['template_dir']}\n"
            summary += f"- 匹配模式: {result['statistics']['pattern']}\n"
            summary += f"- 扫描文件数: {result['statistics']['total_files']}\n"
            summary += f"- 发现宏总数: {result['statistics']['total_macros']}\n\n"
            
            # 按文件显示宏详情
            for file_path, macros in result['grouped_by_file'].items():
                summary += f"=== {file_path} ===\n"
                for macro in macros:
                    args_str = ', '.join(macro['args']) if macro['args'] else '无参数'
                    summary += f"- {macro['name']}({args_str})"
                    if macro['description']:
                        summary += f" - {macro['description']}"
                    summary += "\n"
                summary += "\n"
            
            return summary
        
        # 创建验证器
        collect_validator = UserFunctionValidator()
        collect_validator.add_param_check_validator(min_args=1, max_args=3)  # template_dir 必需，pattern 和 path_prefix 可选
        
        info_funcs = [
            UserFunctionInfo(
                name="collect_jinja_macros",
                handler=collect_macros_handler,
                validator=collect_validator,
                description="收集指定目录下的所有Jinja2宏定义，返回结构化数据对象。参数：template_dir, pattern='**/*.j2', path_prefix=''"
            ),
            UserFunctionInfo(
                name="collect_jinja_macros_for_defines",
                handler=collect_macros_for_defines_handler,
                validator=collect_validator,
                description="收集指定目录下的所有Jinja2宏定义，返回与defines.j2模板兼容的infos列表。参数：template_dir, pattern='**/*.j2', path_prefix=''"
            ),
            UserFunctionInfo(
                name="collect_jinja_macros_summary",
                handler=collect_macros_summary_handler,
                validator=collect_validator,
                description="收集指定目录下的所有Jinja2宏定义，返回文本摘要。参数：template_dir, pattern='**/*.j2', path_prefix=''"
            )
        ]
        
        return info_funcs

    @classmethod
    def on_plugin_load(cls):
        """插件加载时的初始化操作（可选）"""
        pass

    @classmethod
    def on_plugin_unload(cls):
        """插件卸载时的清理操作（可选）"""
        pass
