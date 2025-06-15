import ast
import inspect
from typing import Callable
from pydantic import BaseModel, ValidationError
from RestrictedPython import compile_restricted, safe_builtins
from RestrictedPython.Eval import default_guarded_getitem


class FunctionSignatureValidator(BaseModel):
    """函数签名验证器"""

    @classmethod
    def validate_function_signature(
        cls, func_str: str, expected_sig: inspect.Signature
    ) -> Callable:
        """
        验证函数签名是否符合预期

        :param func_str: 包含函数定义的字符串
        :param expected_sig: 预期的函数签名
        :return: 验证通过的函数
        :raises: ValidationError 如果验证失败
        """
        # 1. 解析函数定义
        func = cls._extract_function(func_str)

        # 2. 验证函数签名
        cls._validate_signature(func, expected_sig)

        return func

    @classmethod
    def _extract_function(cls, func_str: str) -> Callable:
        """安全地从字符串中提取函数"""
        try:
            # 解析AST
            module_ast = ast.parse(func_str)
        except SyntaxError as e:
            raise ValidationError(f"语法错误: {e}")

        # 查找函数定义
        function_defs = [
            node for node in module_ast.body if isinstance(node, ast.FunctionDef)
        ]

        if not function_defs:
            raise ValidationError("未找到函数定义")

        # 使用第一个函数
        func_ast = function_defs[0]
        func_name = func_ast.name

        # 使用RestrictedPython创建安全环境
        restricted_globals = {
            "__builtins__": safe_builtins,
            "_getitem_": default_guarded_getitem,
            "__name__": "__restricted__",
        }

        # 编译并执行函数定义
        try:
            code = compile_restricted(
                ast.Module([func_ast], type_ignores=[]), "<string>", "exec"
            )
            exec(code, restricted_globals)
            return restricted_globals[func_name]
        except Exception as e:
            raise ValidationError(f"函数提取失败: {e}")

    @classmethod
    def _validate_signature(cls, func: Callable, expected_sig: inspect.Signature):
        """验证函数签名"""

        # 获取实际签名
        actual_sig = inspect.signature(func)

        # 比较实际签名和预期签名
        if actual_sig != expected_sig:
            raise ValidationError(
                f"函数签名不匹配: 预期 {expected_sig}, 实际 {actual_sig}"
            )
