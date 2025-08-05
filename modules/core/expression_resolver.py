import ast
from typing import Any
from modules.core.user_function_resolver import UserFunctionContext
class ExpressionResolver:
    """
    支持f-string风格表达式，将{}内的内容递归调用解析器，其余部分原样拼接。
    其余表达式用ast解析。
    """
    def __init__(self, function_resolver):
        self.function_resolver = function_resolver  # 需要传入UserFunctionResolver实例

    def parse(self, expression: str, context: UserFunctionContext) -> Any:
        def eval_ast(node):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                else:
                    raise ValueError("Only simple function calls are supported")
                args = [eval_ast(arg) for arg in node.args]
                return self.function_resolver._resolve(func_name, context, *args)
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Name):
                # 查找 context.cur_node.data 字典
                if hasattr(context, 'cur_node') and hasattr(context.cur_node, 'data') and isinstance(context.cur_node.data, dict):
                    if node.id in context.cur_node.data:
                        return context.cur_node.data[node.id]
                    else:
                        raise ValueError(f"Unknown variable: {node.id} in {expression}")
                else:
                    raise ValueError(f"Context does not have cur_node.data dict for variable lookup: {node.id}")
            else:
                raise ValueError(f"Unsupported expression: {ast.dump(node)}")
            
        def parse_fstring(expr: str) -> str:
            result = ""
            i = 0
            n = len(expr)
            while i < n:
                if expr[i] == '{':
                    depth = 1
                    j = i + 1
                    while j < n and depth > 0:
                        if expr[j] == '{':
                            depth += 1
                        elif expr[j] == '}':
                            depth -= 1
                        j += 1
                    if depth != 0:
                        raise ValueError("Unmatched '{' in f-string expression")
                    inner = expr[i+1:j-1]
                    try:
                        tree = ast.parse(inner, mode='eval')
                    except Exception as e:
                        raise ValueError(f"Invalid expression: {expression}, error: {e}")
                    value = eval_ast(tree.body)
                    result += str(value)
                    i = j
                else:
                    result += expr[i]
                    i += 1
            return result

        # 只有f-string括号内的内容才parse，其他情况直接原样返回
        if isinstance(expression, str):
            if (expression.startswith('f"') and expression.endswith('"')):
                expr_body = expression[2:-1]
                return parse_fstring(expr_body)
            elif (expression.startswith("f'") and expression.endswith("'")):
                expr_body = expression[2:-1]
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
