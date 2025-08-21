# EB-tresos xdm文件生成解决方案

通过定义不同容器的模板，以及定义模块的yaml节点，实现驱动配置界面xdm文件的生成，以及便捷的节点操作。


## TODO:

- 在UUID上使用随机数生成**唯一**的UUID 
- 部分属性值若不可缺失，添加报错逻辑
- Desc的HTML结构自动生成
- XPath的相对节点路径计算
- IMPLEMENTATIONCONFIGCLASS的m/vclass固定标准

## 属性自动推断

1. v:var下的IMPLEMENTATIONCONFIGCLASS，prefix一定为"v"? 都有可能出现，并不是只有v.

## 工作流程(无逆向)

1. 定义Xdm基础框架，例如`main_page`, `module_def`,`ecu_param_def`, `bsw_module_desc`等, 并填写yaml模板
2. 根据模块内容，定义不同的配置界面基本元素，例如`module_block`, `combo_box`, `check_box`, `input_box`等, 同时填写yaml模板
3. 对于共有的属性，可以通过节点数值引用。
