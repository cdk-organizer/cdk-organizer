"""
Catch Exception decorator for CLI commands.

When any exception is throwed by `InfraRuntimeException` class the console output \
    does not have the stack trace, just the message

#### Usage:

```python
from cdk_organizer.catch_exceptions import catch_exceptions


@catch_exceptions
def myfunction():
    pass
```
"""

import logging
import sys
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)


class InfraRuntimeException(Exception):
    """Default managed runtime exception."""


def catch_exceptions(func: Callable) -> Callable:
    """
    Catches and simplifies expected errors thrown by CLI.

    Args:
        func (Callable): The function which may throw exceptions which should be simplified.

    Returns:
        The decorated function.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        """Invoke function and catches the errors."""
        try:
            result = func(*args, **kwargs)
            return result
        except (InfraRuntimeException) as error:
            logger.error(str(error))
            sys.exit(1)

    return decorated
