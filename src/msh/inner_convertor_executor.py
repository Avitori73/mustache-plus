from .InnerExecutor import InnerExecutor
from .types import Convertor


def exec_inner_convertor(convertor: Convertor, meta: str) -> str:
    """
    执行字符串处理函数

    :param convertors: 内部转换器列表
    :param meta: 参数列表
    :return: 函数执行结果
    """
    result = InnerExecutor.execute(convertor.name, {"value": meta, **convertor.params})

    return result
