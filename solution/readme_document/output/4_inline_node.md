# 数据驱动模版生成器内嵌节点
---
该文档讲解了数据驱动模版生成器的内嵌节点功能，展示如何在`preserved_children_key`中通过完整的模板字典来指定子节点的内容，可以用来简化简单节点的创建

## 特性介绍

匿名数据节点: 支持匿名数据节点，用户可以在`children_key`中定义一个完整模板字典来创建匿名数据节点

## 详细说明

### 内嵌节点

在`preserved_children_key`中，可以通过完整的模板字典来指定子节点的内容。这样可以简化简单节点的创建，
例如在root.yaml:
```yaml
TEMPLATE_PATH: "root_template.j2"
CHILDREN_PATH:
  [
    {
      "TEMPLATE_PATH": "include.j2",
      "CHILDREN_PATH": [],
      "name": "f'{include[0]}'",
    },
    {
      "TEMPLATE_PATH": "include.j2",
      "CHILDREN_PATH": [],
      "name": "f'{include[1]}'",
    },
    {
      "TEMPLATE_PATH": "define.j2",
      "CHILDREN_PATH": [],
      "name": "f'{define.name}'",
      "value": "f'{define.value}'",
    },
  ]
include: ["stdio.h", "stdlib.h"]
define:
  name: "MAX"
  value: 1000

function_exprs:
  - "f'{find_node_by_file_path()}'"
```
这样在渲染时，DataDrivenGenerator会将该字典作为一个完整的子节点进行渲染。同时子节点中所引用的内容，可以向上引用父节点的内容，
例如子节点中的"name": "f'{include[0]}'",将会引用父节点的`include`列表中的第一个元素。



## 输入说明

- **文件树"**: 
```text
==============Serialized File Tree==============
u:/users/enlink/documents/code/python/datadrivenfilegenerator/modules/examples/4_inline_children/source/data/
  define.yaml
  include.yaml
  root.yaml
```

- **数据树**: 构建inline节点的文件树时将会默认以name属性命名
```text
==============Serialized Data Tree==============
root.yaml
  f'{include[0]}'
  f'{include[1]}'
  f'{define.name}'
```


## 输出说明

输出root.yaml的渲染结果。

## 关键内容展示

- **文件构建**: 
```python
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
  expression_preprocess(node)
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
```

- `children_content_init`将初始化数据字典中保留的属性
- `children_content_update`将子节点的内容分组

