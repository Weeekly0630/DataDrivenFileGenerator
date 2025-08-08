# DataDrivenGenerator基础渲染示例
---
该文档讲解了数据驱动模版生成器的基本渲染功能，展示了如何使用数据和模板生成文档。包括命令行参数的使用、配置文件构成、文件构成等内容。

## 特性介绍

数据驱动模板: 由数据处理器及模板引擎构成

## 详细说明

### 数据处理器(Data Handler)

数据处理器是DataDrivenGenerator的一个抽象概念，它负责处理将任意来源的数据读取，转换为`DataNode数据节点`， 并最终提供给DataDrivenGenerator一个完整的数据树。用户可以在入口配置文件中设置`data_handler_type`在支持的数据源中选择(目前只有yaml数据)。

### 模板渲染器(Template Handler)

模板渲染器是DataDrivenGenerator的另一个抽象概念，它负责将数据节点转换为最终的文档内容, 即提供一个接口支持使用某一字典对一个模板进行渲染。 用户可以在入口配置文件中设置`template_type`在支持的模板引擎中选择(目前只有Jinja2模板)。

### 数据驱动模版生成器

进行DataHandler以及TemplateHandler的初始化，流程调度，插件初始化，数据预处理等功能。


## 输入说明

- **输入配置文件**: 
```yaml
data_type: yaml # 选择数据处理器类型
# yaml配置
data_config:
  file_root_path: .\source\data # 数据文件根目录
  file_pattern: ["*.yaml"] # 数据文件匹配模式
  encoding: utf-8 # 数据文件编码

# Jinja配置
template_type: jinja # 选择模板渲染器类型
template_config: 
  template_dir: .\source\template # 模板文件目录
  autoescape: false # Jinja2模板配置

# 选择需要渲染的入口数据文件
pattern:
  - "root.yaml"

output_dir: .\source\output # 输出目录
output_file_extension: xml # 输出文件扩展名

# 在数据文件中，保留的关键字，用以指示一些特殊的渲染行为
preserved_template_key: TEMPLATE_PATH # 指示模板文件路径
preserved_children_key: CHILDREN_PATH # 指示子节点路径

# 在模板文件中，保留的关键字，用以指示一些特殊的渲染行为
preserved_children_content_key: CHILDREN_CONTEXT # 引用子节点内容
```

- **Jinja模板**: Jinja支持在某一文件夹下创建一个环境，后续的所有路径都是相对于该环境的相对路径。即在 yaml中的`preserved_template_key`指示的模板文件路径是相对于template_dir的相对路径。
- **数据文件**: 数据文件包含指定模板所需的全部属性，同时指示子节点。当前所使用的是通过子节点文件路径来指示子节点的方式。 即在yaml中的`preserved_children_key`指示的子节点路径是相对于当前节点的相对文件路径(Windows file path)。

## 输出说明

模板渲染最终将指定的入口文档渲染结果保存到output中，并且固定移除一个拓展名，并附加上指定的输出文件扩展名。

## 关键内容展示

- **入口配置文件**: 
```yaml
data_type: yaml
data_config:
  file_root_path: .\source\data
  file_pattern: ["*.yaml"]
  encoding: utf-8

template_type: jinja
template_config:
  template_dir: .\source\template
  autoescape: false

pattern:
  - "*.yaml"

output_dir: .\source\output
output_file_extension: "xml"

preserved_template_key: TEMPLATE
preserved_children_key: CHILDREN
preserved_children_content_key: CHILDREN_CONTENT
```

- **输入数据(data.yaml)**: 
```yaml
TEMPLATE: template.j2
CHILDREN: 

paragrahs:
  - "Paragrah 1"
  - "Paragrah 2"
  - "Paragrah 3"

titles:
  Title1: This is Title1
  Title2: This is Title2
```

- **输入模板(template.j2)**: 
```jinja2
<html>
    {% for paragrah in paragrahs %}
    <p>{{ paragrah }}</p>
    {% endfor %}

    {% for key, value in titles.items() %}
    <h1>{{key}}</h1>
        <p>{{value}}</p>
    {% endfor %}
</html>
```

- **输出结果(output.xml)**: 
```xml
<html>
    <p>Paragrah 1</p>
    <p>Paragrah 2</p>
    <p>Paragrah 3</p>

    <h1>Title1</h1>
        <p>This is Title1</p>
    <h1>Title2</h1>
        <p>This is Title2</p>
</html>
```
