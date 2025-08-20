这些 `tag='var'` 的不同 `type`，在 EB Tresos DataModel 配置界面中，通常对应如下元素类型：

| type                | 配置界面元素类型           | 说明/举例                         |
|---------------------|---------------------------|-----------------------------------|
| ENUMERATION         | 下拉框（枚举选择）         | 用户选择一个预定义选项            |
| INTEGER             | 数字输入框                 | 用户输入整数                      |
| BOOLEAN             | 复选框/开关                | 用户勾选 true/false               |
| FUNCTION-NAME       | 文本输入框（函数名）        | 用户输入函数名字符串              |
| BOOLEAN_LABEL       | 带标签的复选框/开关         | 显示 true/false 并有描述标签      |
| INTEGER_LABEL       | 带标签的数字输入框          | 显示整数并有描述标签              |
| STRING_LABEL        | 带标签的文本输入框          | 显示字符串并有描述标签            |
| FLOAT               | 浮点数输入框                | 用户输入浮点数                    |
| STRING              | 文本输入框                  | 用户输入字符串                    |
| FLOAT_LABEL         | 带标签的浮点数输入框         | 显示浮点数并有描述标签            |
| ENUMERATION_LABEL   | 带标签的下拉框（枚举选择）   | 显示枚举选项并有描述标签          |

**总结：**
- `*_LABEL` 类型一般是带有描述或提示的输入控件。
- `ENUMERATION`/`ENUMERATION_LABEL` 是下拉选择。
- `BOOLEAN`/`BOOLEAN_LABEL` 是复选框或开关。
- `INTEGER`/`FLOAT`/`STRING` 及其 `*_LABEL` 变体是不同类型的输入框。

这些类型直接决定了配置界面上控件的种类和交互方式。