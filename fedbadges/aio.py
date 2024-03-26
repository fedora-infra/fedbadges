import asyncio
import inspect
import logging
from contextlib import suppress


log = logging.getLogger(__name__)


class Periodic:
    """
    Inspired by https://stackoverflow.com/a/37514633

    This runs a task at intervals of the provided seconds.
    The first run will happen after the first interval, unless `run_now` is set to True in the
    `start()` call.
    For long-running tasks, note that there will be `seconds` between two tasks regardless of when
    the task started.
    """

    def __init__(self, func, seconds: float):
        self.func = func
        self.seconds = seconds
        self.is_started = False
        self._task = None

    async def start(self, run_now=False):
        if not self.is_started:
            self.is_started = True
            if run_now:
                await self._run_func()
            # Start task to call func periodically:
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run_loop(self):
        while True:
            await asyncio.sleep(self.seconds)
            await self._run_func()

    async def _run_func(self):
        try:
            result = self.func()
            if inspect.isawaitable(result):
                await result
        except Exception:
            log.exception("Periodic call failed:")
