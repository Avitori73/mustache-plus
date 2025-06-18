from typing import Callable, Dict
import stringcase


def change_case(value: str, caseType: str) -> str:
    """
    改变字符串的格式
    :param value: 要转换的字符串
    :param caseType: 目标格式类型
    :return: 转换后的字符串
    :raises ValueError: 如果 caseType 不在已知类型中
    """
    match caseType:
        case "camel":
            return stringcase.camelcase(value)
        case "capital":
            return stringcase.capitalcase(value)
        case "const":
            return stringcase.constcase(value)
        case "lower":
            return stringcase.lowercase(value)
        case "pascal":
            return stringcase.pascalcase(value)
        case "path":
            return stringcase.pathcase(value)
        case "sentence":
            return stringcase.sentencecase(value)
        case "snake":
            return stringcase.snakecase(value)
        case "spinal":
            return stringcase.spinalcase(value)
        case "title":
            return stringcase.titlecase(value)
        case "trim":
            return stringcase.trimcase(value)
        case "upper":
            return stringcase.uppercase(value)
        case "alphanum":
            return stringcase.alphanumcase(value)
        case _:
            raise ValueError(f"change_case unknown caseType: {caseType}")


def substr(value: str, start: int = None, end: int = None) -> str:
    """
    截取字符串的子串
    :param value: 要截取的字符串
    :param start: 起始索引（默认为 None，表示从开头开始）
    :param end: 结束索引（默认为 None，表示直到字符串末尾）
    :return: 截取后的子串
    """
    return value[start:end]


inner_convertors: Dict[str, Callable[..., str]] = {
    "change_case": change_case,
    "substr": substr,
}
