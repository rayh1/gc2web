from threading import Lock
from typing import Any, TypeVar, cast

T = TypeVar('T')

def singleton(cls: T) -> T:
    """
    A thread-safe singleton decorator.
    
    Usage:
        @singleton
        class MyClass:
            pass
    """
    _instance = {}
    _lock = Lock()
    
    def get_instance(*args: Any, **kwargs: Any) -> T:
        with _lock:
            if cls not in _instance:
                _instance[cls] = cls(*args, **kwargs) # type: ignore
            return cast(T, _instance[cls])
            
    return cast(T, get_instance)