# 插件函数使用文档

本文档包含所有可用的插件函数及其使用方法。

## 目录

### 按类别浏览
- [Node 类函数](#node-类函数)
- [XdmA 类函数](#xdma-类函数)
- [XdmAttribute 类函数](#xdmattribute-类函数)

### 所有函数列表
- [node_find_create](#node-find-create)
- [node_value_create](#node-value-create)
- [xdma_bswmoduledescblock_create](#xdma-bswmoduledescblock-create)
- [xdma_ecuparamdefblock_create](#xdma-ecuparamdefblock-create)
- [xdma_field_create](#xdma-field-create)
- [xdma_fieldmeta_create](#xdma-fieldmeta-create)
- [xdma_mainpage_create](#xdma-mainpage-create)
- [xdma_moduledefblock_create](#xdma-moduledefblock-create)
- [xdma_referencefield_create](#xdma-referencefield-create)
- [xdma_table_create](#xdma-table-create)
- [xdma_tablerow_create](#xdma-tablerow-create)
- [xdmattribute_node_create](#xdmattribute-node-create)

---

## 函数收集摘要

- **总函数数**: 12
- **成功收集的类**: Node, XdmA, XdmAttribute
- **发现的类**: Node, XdmA, XdmAttribute

---

## Node 类函数

来源类：`Node`  
函数数量：2

### 函数列表
- [node_find_create](#node-find-create)
- [node_value_create](#node-value-create)

<a id="node-find-create"></a>
### node_find_create

**描述**：查找数据节点的结果

**参数列表**：
- `results`: Any
  - 任意类型



**函数签名**：
```python
node_find_create(results: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{node_find_create(
    <results_value>)}"
```

*带参数名的调用：*
```yaml
data: "{node_find_create(
    results=<results_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{node_find_create('results_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {node_find_create('demo')}"
```


---
<a id="node-value-create"></a>
### node_value_create

**描述**：引用节点值的元数据

**参数列表**：
- `value`: Any
  - 任意类型



**函数签名**：
```python
node_value_create(value: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{node_value_create(
    <value_value>)}"
```

*带参数名的调用：*
```yaml
data: "{node_value_create(
    value=<value_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{node_value_create('value_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {node_value_create('demo')}"
```


---
## XdmA 类函数

来源类：`XdmA`  
函数数量：9

### 函数列表
- [xdma_bswmoduledescblock_create](#xdma-bswmoduledescblock-create)
- [xdma_ecuparamdefblock_create](#xdma-ecuparamdefblock-create)
- [xdma_field_create](#xdma-field-create)
- [xdma_fieldmeta_create](#xdma-fieldmeta-create)
- [xdma_mainpage_create](#xdma-mainpage-create)
- [xdma_moduledefblock_create](#xdma-moduledefblock-create)
- [xdma_referencefield_create](#xdma-referencefield-create)
- [xdma_table_create](#xdma-table-create)
- [xdma_tablerow_create](#xdma-tablerow-create)

<a id="xdma-bswmoduledescblock-create"></a>
### xdma_bswmoduledescblock_create

**描述**：MetaData()

无参数



**函数签名**：
```python
xdma_bswmoduledescblock_create()
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_bswmoduledescblock_create(
)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_bswmoduledescblock_create(
)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_bswmoduledescblock_create()}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_bswmoduledescblock_create()}"
```


---
<a id="xdma-ecuparamdefblock-create"></a>
### xdma_ecuparamdefblock_create

**描述**：MetaData()

无参数



**函数签名**：
```python
xdma_ecuparamdefblock_create()
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_ecuparamdefblock_create(
)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_ecuparamdefblock_create(
)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_ecuparamdefblock_create()}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_ecuparamdefblock_create()}"
```


---
<a id="xdma-field-create"></a>
### xdma_field_create

**描述**：MetaData()

无参数



**函数签名**：
```python
xdma_field_create()
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_field_create(
)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_field_create(
)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_field_create()}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_field_create()}"
```


---
<a id="xdma-fieldmeta-create"></a>
### xdma_fieldmeta_create

**描述**：MetaData()

无参数



**函数签名**：
```python
xdma_fieldmeta_create()
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_fieldmeta_create(
)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_fieldmeta_create(
)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_fieldmeta_create()}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_fieldmeta_create()}"
```


---
<a id="xdma-mainpage-create"></a>
### xdma_mainpage_create

**描述**：MetaData(xml_version: str, namespaces: Dict[str, str], project: Optional[str], platform: Optional[str], peripheral: Optional[str], autosar_version: Optional[str], build_version: Optional[str], copyright: Optional[str], ctr_type: str, ctr_factory: str, ctr_namespaces: Dict[str, str], top_level_package_name: Optional[str], top_level_package_type: Optional[str], uuid_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData)

**参数列表**：
- `xml_version`: Any
  - 任意类型
- `namespaces`: Any
  - 任意类型
- `project`: Any
  - 任意类型
- `platform`: Any
  - 任意类型
- `peripheral`: Any
  - 任意类型
- `autosar_version`: Any
  - 任意类型
- `build_version`: Any
  - 任意类型
- `copyright`: Any
  - 任意类型
- `ctr_type`: Any
  - 任意类型
- `ctr_factory`: Any
  - 任意类型
- `ctr_namespaces`: Any
  - 任意类型
- `top_level_package_name`: Any
  - 任意类型
- `top_level_package_type`: Any
  - 任意类型
- `uuid_attr_xml`: Any
  - 任意类型



**函数签名**：
```python
xdma_mainpage_create(xml_version: Any, namespaces: Any, project: Any, platform: Any, peripheral: Any, autosar_version: Any, build_version: Any, copyright: Any, ctr_type: Any, ctr_factory: Any, ctr_namespaces: Any, top_level_package_name: Any, top_level_package_type: Any, uuid_attr_xml: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_mainpage_create(
    <xml_version_value>,
    <namespaces_value>,
    <project_value>,
    <platform_value>,
    <peripheral_value>,
    <autosar_version_value>,
    <build_version_value>,
    <copyright_value>,
    <ctr_type_value>,
    <ctr_factory_value>,
    <ctr_namespaces_value>,
    <top_level_package_name_value>,
    <top_level_package_type_value>,
    <uuid_attr_xml_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_mainpage_create(
    xml_version=<xml_version_value>,
    namespaces=<namespaces_value>,
    project=<project_value>,
    platform=<platform_value>,
    peripheral=<peripheral_value>,
    autosar_version=<autosar_version_value>,
    build_version=<build_version_value>,
    copyright=<copyright_value>,
    ctr_type=<ctr_type_value>,
    ctr_factory=<ctr_factory_value>,
    ctr_namespaces=<ctr_namespaces_value>,
    top_level_package_name=<top_level_package_name_value>,
    top_level_package_type=<top_level_package_type_value>,
    uuid_attr_xml=<uuid_attr_xml_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_mainpage_create('xml_version_value', 'namespaces_value', 'project_value', 'platform_value', 'peripheral_value', 'autosar_version_value', 'build_version_value', 'copyright_value', 'ctr_type_value', 'ctr_factory_value', 'ctr_namespaces_value', 'top_level_package_name_value', 'top_level_package_type_value', 'uuid_attr_xml_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_mainpage_create('demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
<a id="xdma-moduledefblock-create"></a>
### xdma_moduledefblock_create

**描述**：MetaData(name: str, release_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, admin_data_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, postbuildvariantsupport_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, desc_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, lower_multiplicity_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, upper_multiplicity_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, uuid_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, imp_desc_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, imp_implementationconfigclass_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, imp_label_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, imp_uuid_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, imp_default_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, imp_range_attr_xml: modules.utils.type_classes.xml.XmlNode.MetaData, refind_module_def_value: str)

**参数列表**：
- `name`: str
  - 名称字符串
- `release_attr_xml`: Any
  - 任意类型
- `admin_data_attr_xml`: Any
  - 任意类型
- `postbuildvariantsupport_attr_xml`: Any
  - 任意类型
- `desc_attr_xml`: Any
  - 任意类型
- `lower_multiplicity_attr_xml`: Any
  - 任意类型
- `upper_multiplicity_attr_xml`: Any
  - 任意类型
- `uuid_attr_xml`: Any
  - 任意类型
- `imp_desc_attr_xml`: Any
  - 任意类型
- `imp_implementationconfigclass_attr_xml`: Any
  - 任意类型
- `imp_label_attr_xml`: Any
  - 任意类型
- `imp_uuid_attr_xml`: Any
  - 任意类型
- `imp_default_attr_xml`: Any
  - 任意类型
- `imp_range_attr_xml`: Any
  - 任意类型
- `refind_module_def_value`: Any
  - 任意类型



**函数签名**：
```python
xdma_moduledefblock_create(name: str, release_attr_xml: Any, admin_data_attr_xml: Any, postbuildvariantsupport_attr_xml: Any, desc_attr_xml: Any, lower_multiplicity_attr_xml: Any, upper_multiplicity_attr_xml: Any, uuid_attr_xml: Any, imp_desc_attr_xml: Any, imp_implementationconfigclass_attr_xml: Any, imp_label_attr_xml: Any, imp_uuid_attr_xml: Any, imp_default_attr_xml: Any, imp_range_attr_xml: Any, refind_module_def_value: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_moduledefblock_create(
    <name_value>,
    <release_attr_xml_value>,
    <admin_data_attr_xml_value>,
    <postbuildvariantsupport_attr_xml_value>,
    <desc_attr_xml_value>,
    <lower_multiplicity_attr_xml_value>,
    <upper_multiplicity_attr_xml_value>,
    <uuid_attr_xml_value>,
    <imp_desc_attr_xml_value>,
    <imp_implementationconfigclass_attr_xml_value>,
    <imp_label_attr_xml_value>,
    <imp_uuid_attr_xml_value>,
    <imp_default_attr_xml_value>,
    <imp_range_attr_xml_value>,
    <refind_module_def_value_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_moduledefblock_create(
    name=<name_value>,
    release_attr_xml=<release_attr_xml_value>,
    admin_data_attr_xml=<admin_data_attr_xml_value>,
    postbuildvariantsupport_attr_xml=<postbuildvariantsupport_attr_xml_value>,
    desc_attr_xml=<desc_attr_xml_value>,
    lower_multiplicity_attr_xml=<lower_multiplicity_attr_xml_value>,
    upper_multiplicity_attr_xml=<upper_multiplicity_attr_xml_value>,
    uuid_attr_xml=<uuid_attr_xml_value>,
    imp_desc_attr_xml=<imp_desc_attr_xml_value>,
    imp_implementationconfigclass_attr_xml=<imp_implementationconfigclass_attr_xml_value>,
    imp_label_attr_xml=<imp_label_attr_xml_value>,
    imp_uuid_attr_xml=<imp_uuid_attr_xml_value>,
    imp_default_attr_xml=<imp_default_attr_xml_value>,
    imp_range_attr_xml=<imp_range_attr_xml_value>,
    refind_module_def_value=<refind_module_def_value_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_moduledefblock_create('example_name', 'release_attr_xml_value', 'admin_data_attr_xml_value', 'postbuildvariantsupport_attr_xml_value', 'desc_attr_xml_value', 'lower_multiplicity_attr_xml_value', 'upper_multiplicity_attr_xml_value', 'uuid_attr_xml_value', 'imp_desc_attr_xml_value', 'imp_implementationconfigclass_attr_xml_value', 'imp_label_attr_xml_value', 'imp_uuid_attr_xml_value', 'imp_default_attr_xml_value', 'imp_range_attr_xml_value', 'refind_module_def_value_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_moduledefblock_create('demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo', 'demo')}"
```


---
<a id="xdma-referencefield-create"></a>
### xdma_referencefield_create

**描述**：MetaData()

无参数



**函数签名**：
```python
xdma_referencefield_create()
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_referencefield_create(
)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_referencefield_create(
)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_referencefield_create()}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_referencefield_create()}"
```


---
<a id="xdma-table-create"></a>
### xdma_table_create

**描述**：MetaData()

无参数



**函数签名**：
```python
xdma_table_create()
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_table_create(
)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_table_create(
)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_table_create()}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_table_create()}"
```


---
<a id="xdma-tablerow-create"></a>
### xdma_tablerow_create

**描述**：MetaData()

无参数



**函数签名**：
```python
xdma_tablerow_create()
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdma_tablerow_create(
)}"
```

*带参数名的调用：*
```yaml
data: "{xdma_tablerow_create(
)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdma_tablerow_create()}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdma_tablerow_create()}"
```


---
## XdmAttribute 类函数

来源类：`XdmAttribute`  
函数数量：1

### 函数列表
- [xdmattribute_node_create](#xdmattribute-node-create)

<a id="xdmattribute-node-create"></a>
### xdmattribute_node_create

**描述**：Xdm Attribute Metadata

**参数列表**：
- `name`: str
  - 名称字符串
- `metadata`: Any
  - 任意类型



**函数签名**：
```python
xdmattribute_node_create(name: str, metadata: Any)
```

**YAML 使用模板**：

*简单调用：*
```yaml
data: "{xdmattribute_node_create(
    <name_value>,
    <metadata_value>)}"
```

*带参数名的调用：*
```yaml
data: "{xdmattribute_node_create(
    name=<name_value>,
    metadata=<metadata_value>)
}"
```


**使用示例**：
```yaml
# 示例 1：基本使用
example1: "{xdmattribute_node_create('example_name', 'metadata_value')}"

# 示例 2：在 f-string 中使用
example2: f"结果: {xdmattribute_node_create('demo', 'demo')}"
```


---

## 使用指南

### 基本语法

1. **在表达式中使用**：
   ```yaml
   data: "{function_name(param1, param2)}"
   ```

2. **在 f-string 中使用**：
   ```yaml
   data: f"结果是 {function_name(param1, param2)}"
   ```

3. **嵌套函数调用**：
   ```yaml
   data: "{outer_function(inner_function(param1), param2)}"
   ```

### 参数类型说明

- **str**: 字符串，需要用引号包围，如 `'example'`
- **int**: 整数，直接写数字，如 `42`
- **bool**: 布尔值，使用 `true` 或 `false`
- **List**: 列表，使用 `[]` 语法，如 `['item1', 'item2']`
- **Plugin类型**: 其他插件函数的返回值，可以嵌套调用

### 转义字符

在 YAML 中使用函数时，需要对大括号进行转义：
- 使用 `\\{` 替代 `{`
- 使用 `}\\` 替代 `}`

### 常见模式

1. **创建对象**：
   ```yaml
   object: "{create_function('name', 'type')}"
   ```

2. **嵌套对象**：
   ```yaml
   complex_object: "{parent_create(
     child=child_create('child_name'),
     other_param='value'
   )}"
   ```

3. **列表操作**：
   ```yaml
   list_data: "{list_function(['item1', 'item2', 'item3'])}"
   ```

## 附录

### 生成信息

- 总函数数：12
- 成功收集的类：Node, XdmA, XdmAttribute
