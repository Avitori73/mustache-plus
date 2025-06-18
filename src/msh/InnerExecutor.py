from inspect import signature
from typing import Any, Callable, Dict
from .inner_convertor import inner_convertors


def call_inner_convertor(
    name: str,
    parameters: Dict[str, Any],
) -> str:
    callable = get_callable(name)
    validate_parameters(callable, parameters)
    return callable(**parameters)


def validate_parameters(
    callable: Callable[..., str], parameters: Dict[str, Any]
) -> None:
    # 获取 callable 的参数列表
    sig = signature(callable)
    sig_params = sig.parameters
    # 检查 parameters 中的每个参数和类型是否匹配 callable 的参数
    for param_name, param_value in parameters.items():
        if param_name not in sig_params:
            raise ValueError(
                f"Parameter '{param_name}' is not a valid parameter for the callable."
            )
        expected_type = sig_params[param_name].annotation
        if expected_type is not Any and not isinstance(param_value, expected_type):
            raise TypeError(
                f"Parameter '{param_name}' must be of type {expected_type}, got {type(param_value)} instead."
            )


def get_callable(name: str) -> Callable[..., str]:
    """
    获取一个可以调用的函数
    :param name: 函数名称
    :return: 可调用的函数
    """
    if name in inner_convertors:
        return inner_convertors[name]
    else:
        raise ValueError(f"Function {name} not found in inner convertors.")


class InnerExecutor:
    """内置转化器执行器"""

    @staticmethod
    def execute(name: str, parameters: Dict[str, Any]) -> str:
        return call_inner_convertor(name, parameters)


if __name__ == "__main__":
    # Example usage
    try:
        result = InnerExecutor.execute(
            "change_case", {"value": "hello_world", "caseType": "upper"}
        )
        print(result)
    except Exception as e:
        print(f"Error: {e}")
