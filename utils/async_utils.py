import asyncio

def run_async(coroutine_func, *args, **kwargs):
    """
    Runs an asynchronous coroutine and waits for its result.

    This utility function ensures that an asynchronous coroutine is properly 
    executed and awaited, handling both running in an existing event loop 
    and setting up a new one when necessary.

    If the event loop is already running (for example, in a web framework or 
    interactive environment like Jupyter), the coroutine is scheduled as a 
    task using `asyncio.ensure_future()`. If the event loop is not running, 
    it creates a new event loop to run the coroutine to completion.

    Parameters:
        coroutine_func (Callable): An asynchronous function (coroutine) that 
                                    takes arbitrary arguments and returns a result.
        *args: Variable length argument list to be passed to the coroutine.
        **kwargs: Arbitrary keyword arguments to be passed to the coroutine.

    Returns:
        Any: The result returned by the coroutine after it is awaited, 
             which could be of any type depending on the coroutine's return value.

    Raises:
        RuntimeError: If the coroutine cannot be executed (for example, 
                      if the event loop is broken).
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    coroutine = coroutine_func(*args, **kwargs)

    if loop.is_running():
        future = asyncio.ensure_future(coroutine)
        return asyncio.get_event_loop().run_until_complete(future)
    else:
        return loop.run_until_complete(coroutine)