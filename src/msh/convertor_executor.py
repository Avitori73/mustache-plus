from typing import Dict
from .FunctionSignatureValidator import FunctionSignatureValidator
from .SafeExecutor import SafeExecutor
import inspect


def exec_convertor(
    func_str: str,
    params: Dict[str, str],
) -> str:
    """
    执行字符串处理函数

    :param func_str: 包含函数定义的字符串
    :param params: 参数列表
    :return: 函数执行结果
    """

    # 1. 安全地从字符串中提取函数
    convertor_expected_sig = inspect.Signature(
        parameters=[
            inspect.Parameter("params", inspect.Parameter.POSITIONAL_OR_KEYWORD),
        ],
        return_annotation=str,
    )
    func = FunctionSignatureValidator.validate_function_signature(
        func_str, convertor_expected_sig
    )

    # 2. 执行函数
    result = SafeExecutor.execute(func, [params])

    # 3. 渲染结果如果是空字符串，则返回 None
    if result == "":
        return None

    return result
