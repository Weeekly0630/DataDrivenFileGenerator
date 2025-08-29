import ast
from typing import Any, Optional
from modules.core.user_function_resolver import UserFunctionContext


class ExpressionResolver:
    """
    支持f-string风格表达式，将{}内的内容递归调用解析器，其余部分原样拼接。
    其余表达式用ast解析。
    """

    def __init__(self, function_resolver):
        self.function_resolver = function_resolver  # 需要传入UserFunctionResolver实例

    def parse(self, expression: str, context: UserFunctionContext) -> Any:
        def eval_ast(node, local_vars=None):
            local_vars = local_vars or {}

            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                else:
                    raise ValueError("Only simple function calls are supported")
                args = [eval_ast(arg, local_vars) for arg in node.args]
                kwargs = {kw.arg: eval_ast(kw.value, local_vars) for kw in node.keywords}
                return self.function_resolver._resolve(
                    func_name, context, *args, **kwargs
                )
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.List):
                return [eval_ast(elt, local_vars) for elt in node.elts]
            elif isinstance(node, ast.ListComp):
                def eval_list_comp(node, outer_vars):
                    # 如果没有生成器，直接返回结果
                    if not node.generators:
                        return eval_ast(node.elt, outer_vars)
                    
                    result = []
                    gen = node.generators[0]  # 处理当前层的生成器
                    
                    # 评估迭代器，使用外层作用域
                    iter_values = eval_ast(gen.iter, outer_vars)
                    
                    # 处理条件（if子句）
                    def check_conditions(val, conditions, local_scope):
                        for cond in conditions:
                            if not eval_ast(cond, local_scope):
                                return False
                        return True
                    
                    for val in iter_values:
                        # 创建新的作用域，包含外层变量
                        current_vars = outer_vars.copy()
                        current_vars[gen.target.id] = val
                        
                        # 检查if条件
                        if not check_conditions(val, gen.ifs, current_vars):
                            continue
                            
                        if len(node.generators) > 1:
                            # 递归处理剩余的生成器
                            next_comp = ast.ListComp(
                                elt=node.elt,
                                generators=node.generators[1:]
                            )
                            result.extend(eval_list_comp(next_comp, current_vars))
                        else:
                            # 到达最内层，计算结果表达式
                            def deep_eval(n):
                                if isinstance(n, ast.Tuple):
                                    return tuple(deep_eval(elt) for elt in n.elts)
                                elif isinstance(n, ast.List):
                                    return [deep_eval(elt) for elt in n.elts]
                                elif isinstance(n, ast.Name):
                                    if n.id in current_vars:
                                        return current_vars[n.id]
                                    return eval_ast(n, current_vars)
                                else:
                                    return eval_ast(n, current_vars)
                                    
                            result.append(deep_eval(node.elt))
                            
                    return result
                
                # 使用当前作用域作为初始外层作用域
                return eval_list_comp(node, local_vars or {})
            elif isinstance(node, ast.Tuple):
                return tuple(eval_ast(elt, local_vars) for elt in node.elts)
            elif isinstance(node, ast.Dict):
                return {
                    eval_ast(k, local_vars): eval_ast(v, local_vars) for k, v in zip(node.keys, node.values)
                }
            elif isinstance(node, ast.Name):
                # 支持作用域链，向上查找 cur_node 的父节点
                from modules.node.data_node import DataNode
                from modules.node.file_node import BaseNode

                def lookup_variable(cur_node: Optional[DataNode], varname: str) -> Any:
                    """在当前节点及其父节点中查找变量"""
                    while cur_node is not None:
                        if varname in cur_node.data:
                            return cur_node.data[varname]
                        parent_base_node: Optional[BaseNode] = (
                            cur_node._parent._parent.parent
                        )
                        if parent_base_node:
                            cur_node = parent_base_node.mapping_obj
                        else:
                            cur_node = None

                    raise ValueError(f"Unknown variable: {varname} in {expression}")

                if node.id in local_vars:
                    return local_vars[node.id]
                if hasattr(context, "cur_node"):
                    return lookup_variable(context.cur_node, node.id)
                else:
                    raise ValueError(
                        f"Context does not have cur_node for variable lookup: {node.id}"
                    )
            elif isinstance(node, ast.Attribute):
                # 支持 define.name 这种多层变量引用
                value = eval_ast(node.value, local_vars)
                if isinstance(value, dict) and node.attr in value:
                    return value[node.attr]
                elif hasattr(value, node.attr):
                    return getattr(value, node.attr)
                else:
                    raise ValueError(f"Attribute '{node.attr}' not found in {value}")
            elif isinstance(node, ast.Subscript):
                # 支持 include[1]、a['key'] 等下标访问
                value = eval_ast(node.value, local_vars)
                # 兼容 Python 3.8 及更早和 3.9+ 的 slice 表达式
                slice_node = node.slice
                # Python <3.9: ast.Index; Python 3.9+: 直接是表达式
                if hasattr(ast, "Index") and isinstance(slice_node, ast.Index):
                    index = eval_ast(slice_node.value, local_vars)
                else:
                    # 3.9+ 直接是表达式（如ast.Constant/ast.Name/ast.Num等）
                    index = (
                        eval_ast(slice_node, local_vars)
                        if isinstance(slice_node, ast.AST)
                        else slice_node
                    )
                return value[index]
            else:
                raise ValueError(f"Unsupported expression: {ast.dump(node)}")

        def preprocess_braces(s: str) -> str:
            # 先把转义的 \{ 和 \} 替换成特殊标记
            return s.replace(r"\{", "__LEFT_BRACE__").replace(r"\}", "__RIGHT_BRACE__")

        def postprocess_braces(s: str) -> str:
            # 处理完表达式后再替换回来
            return s.replace("__LEFT_BRACE__", "{").replace("__RIGHT_BRACE__", "}")

        def safe_eval_fstring(expr: str) -> str:
            """
            尝试将 f-string 表达式安全地解析为字符串。
            如果解析失败，则警告并返回原始字符串。
            """
            # 先处理转义
            expr = preprocess_braces(expr)
            try:
                tree = ast.parse(expr, mode="eval")
                value = eval_ast(tree.body)
            except Exception as e:
                print(f"[警告] Invalid expression: {expr}, error: {e}")
                value = expr
            # 还原转义
            return postprocess_braces(str(value))

        def parse_fstring(expr: str) -> str:
            # 先处理转义
            expr = preprocess_braces(expr)
            result = ""
            i = 0
            n = len(expr)
            while i < n:
                if expr[i] == "{":
                    depth = 1
                    j = i + 1
                    while j < n and depth > 0:
                        if expr[j] == "{":
                            depth += 1
                        elif expr[j] == "}":
                            depth -= 1
                        j += 1
                    if depth != 0:
                        raise ValueError("Unmatched '{' in f-string expression")
                    inner = expr[i + 1 : j - 1]
                    value = safe_eval_fstring(inner)
                    result += str(value)
                    i = j
                else:
                    result += expr[i]
                    i += 1
            # 还原转义
            return postprocess_braces(result)

        # 只有f-string括号内的内容才parse，其他情况直接原样返回
        if isinstance(expression, str):
            expr = expression.strip()  # 新增：去除首尾空白字符

            # 新增：如果以{开头且以}结尾，直接解析内容并返回原始对象
            if expr.startswith("{") and expr.endswith("}"):
                inner = expr[1:-1].strip()
                try:
                    tree = ast.parse(inner, mode="eval")
                except Exception as e:
                    raise ValueError(f"Invalid expression: {expression}, error: {e}")
                return eval_ast(tree.body)
            elif expr.startswith('f"') and expr.endswith('"'):
                expr_body = expr[2:-1]
                return parse_fstring(expr_body)
            elif expr.startswith("f'") and expr.endswith("'"):
                expr_body = expr[2:-1]
                return parse_fstring(expr_body)
            else:
                return expression


# --- 简单测试 ---
if __name__ == "__main__":

    class DummyContext:
        pass

    class DummyFunctionResolver:
        def _resolve(self, func_name, context, *args):
            if func_name == "add":
                return int(args[0]) + int(args[1])
            if func_name == "mul":
                return int(args[0]) * int(args[1])
            raise ValueError(f"Unknown function: {func_name}")

    resolver = ExpressionResolver(DummyFunctionResolver())
    ctx = DummyContext()
    print(resolver.parse("add(2, 3)", ctx))  # 5
    print(resolver.parse("mul(add(2, 3), 4)", ctx))  # 20
    print(resolver.parse("f'hello {add(1,2)} world'", ctx))  # hello 3 world
    print(resolver.parse("f'{mul(2, 3)} + {add(4, 5)}'", ctx))  # 6 + 9
