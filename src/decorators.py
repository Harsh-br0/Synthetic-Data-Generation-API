import functools
import time
from typing import Callable, Iterable

from .logging import logger

log = logger(__name__)


def handle_errors(errs: dict[Exception, Callable[[Exception], Exception]]):

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.exception("Caught this err in decorator..")

                for cls in type(e).__mro__:  # check all parent classes of error for handler
                    if cls in errs:
                        raise errs[cls](e)

                raise e  # re raise the error to handle on main app

        return wrapper

    return decorator


def retry(errs: Iterable[Exception], retry: int = 2, delay: float = 1.7):
    errs = set(errs)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_processed, is_matched = False, False

            for attempt in range(retry):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if not is_processed:
                        is_processed = True

                        # check all parent classes of error for retrying
                        for cls in type(e).__mro__:
                            if cls in errs:
                                is_matched = True
                                break

                    if is_matched and attempt < retry:
                        log.info("Sleeping on func '%s' for %s secs", func.__name__, delay)
                        time.sleep(delay)
                    else:
                        raise e  # re raise the error to handle on main app

        return wrapper

    return decorator
