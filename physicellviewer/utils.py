from time import time
import asyncio

from ipywidgets import Output

class Timer:
    """
    Utility function used to call run a function after a specified amount of time.
    From Jypyter documentation https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html#Debouncing
    
    """
    
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback

    async def _job(self):
        await asyncio.sleep(self._timeout)
        self._callback()

    def start(self):
        self._task = asyncio.ensure_future(self._job())

    def cancel(self):
        self._task.cancel()

def debounce(wait):
    """ 
    Utility function used to call run a function after a specified amount of time.
    Based on Jypyter documentation https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html#Debouncing
    
    Decorator which debounces a function call for a specified amount of time or until it has been longer than 
    the specified amount of time since the function was last called.
    """
    def decorator(fn):
        timer = None
        lastCall = time()
        def debounced(*args, **kwargs):
            nonlocal timer
            nonlocal lastCall
            def call_it():
                fn(*args, **kwargs)
            if timer is not None:
                timer.cancel()
            if time() - lastCall >= wait:
                lastCall = time()
                if timer is not None:
                    timer.cancel()
                call_it()
            else:
                timer = Timer(wait, call_it)
                timer.start()
        return debounced
    return decorator

output = Output()