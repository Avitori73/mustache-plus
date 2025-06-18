from typing import Any, List, Callable
from pydantic import validate_arguments
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import sys

try:
    import resource

    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False


def set_memory_limit(memory_limit):
    if HAS_RESOURCE and sys.platform != "win32":
        try:
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
        except Exception:
            # 可记录日志或忽略
            pass
    else:
        # Windows 或不支持 resource，跳过或用其他方式
        pass


class SafeExecutor:
    """安全的函数执行器"""

    @staticmethod
    def execute(
        func: Callable,
        params: List[Any] = [],
        timeout: float = 5.0,
        memory_limit: int = 50 * 1024 * 1024,  # 50MB
    ) -> str:
        """
        安全执行函数

        :param func: 要执行的函数
        :param params: 参数列表
        :param timeout: 执行超时(秒)
        :param memory_limit: 内存限制(字节)
        :return: 函数执行结果
        :raises: TimeoutError, MemoryError, RuntimeError
        """

        # 带资源限制的函数包装
        @validate_arguments
        def restricted_func(params: List[Any]) -> Any:
            # 设置内存限制，windows 下无效
            set_memory_limit(memory_limit)
            return func(*params)

        # 使用线程池设置超时
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(restricted_func, params)
            try:
                return future.result(timeout=timeout)
            except TimeoutError as e:
                raise TimeoutError(f"执行超时 ({timeout} 秒)") from e
            except MemoryError as e:
                raise MemoryError(f"超出内存限制 ({memory_limit} 字节)") from e
            except Exception as e:
                raise RuntimeError(f"执行错误: {e}") from e
