# Clang CIndex Python 接口

本模块基于 libclang，自动化解析 C/C++ 源码，提取结构化声明与预处理信息，适用于代码分析、自动文档生成等场景。

---

## 能力与适用范围

- **完整性**：Clang 能够完整描述 C 语言的语法结构，包括所有类型声明、变量、函数、结构体、联合体、枚举、typedef、注释、源码位置等。AST 节点信息丰富，适合做静态分析、代码生成、文档提取等。
- **节点信息**：每个 AST 节点（Cursor）包含如下典型属性：
  - spelling（名称）
  - kind（节点类型，如 VAR_DECL、STRUCT_DECL 等）
  - type（类型信息，含指针、数组、限定符等）
  - storage_class（存储类型，如 static、extern）
  - location（文件、行、列）
  - raw_comment / brief_comment（注释）
  - extent（源码范围，可提取原始代码片段）
- **C 语言支持**：Clang 的 AST 能完整覆盖 C 语言标准语法，绝大多数 C 代码结构都能被准确还原和遍历。

---

## 工作流程

```mermaid
graph TD
    A[输入C文件] --> B[使用Clang生成AST]
    B --遍历AST--> C[获取Decl节点]
    C --> D[提取关键信息，生成对应类实例]
    D --> E[返回给yaml expr预处理]
    E --> F[进行后续渲染]
```

---

## 变量节点属性示例

假设有如下 C 代码：

```c
// 全局变量，带注释
static const int g_value = 42;
```

其 Clang AST Cursor 节点属性与 C 代码的对应关系如下：

| C 代码内容   | Cursor 属性               | 示例值                         |
| ------------ | ------------------------- | ------------------------------ |
| 名称         | spelling                  | g_value                        |
| 节点类型     | kind                      | VAR_DECL                       |
| 类型         | type.spelling             | const int                      |
| 存储类型     | storage_class             | STATIC                         |
| 限定符       | type.is_const_qualified() | True                           |
| 初始化表达式 | init_expr                 | 42                             |
| 注释         | raw_comment/brief_comment | // 全局变量，带注释            |
| 代码片段     | extend                  | static const int g_value = 42; |

---

## 宏与预处理指令支持及局限

- **支持内容**：
  - #define 宏定义（名称、参数、值）
  - #include 包含指令（文件名、是否系统头文件）
  - 宏实例化（宏展开点、参数）
- **局限性**：
  - 条件编译指令（#ifdef/#ifndef/#if/#elif/#else/#endif）不会出现在 AST 中，无法直接提取条件编译结构。
  - 宏展开仅能获取到宏实例化点及参数，无法还原复杂的宏替换逻辑。
  - 预处理流程本身（如 include 路径搜索、宏递归替换等）不在 AST 结果中体现。



---

## 典型用法

```python
from modules.plugins.clang.extractor import ClangExtractor

extractor = ClangExtractor("libclang.dll 路径")
result = extractor.extract(
    "test.c",
    c_args=["-Iinclude_path"],
    debug_level=1,
    main_file_only=True,
    user_macro_only=True,
)
print(result["structs"])
print(result["variables"])
print(result["preprocessing"]["macro_definitions"])
```

---

## 依赖

- Python clang 包（pip install clang）
- libclang 动态库

详细参数与扩展用法见 extractor.py 注释。

## 可能的问题

- 宏不展开：
   - **需求**：宏定义不展开，需要一个宏定义未展开的代码，例如`int a = MAX;`。
   - **问题的原因**: Clang AST 树中的值为宏展开后的值，无法直接获取未展开的宏定义。
   - **解决方案**：对于需要获取未展开代码的场景，可以使用`cursor.extend`获取源文件代码。
