import asyncio
import inspect
import logging
from contextlib import suppress


log = logging.getLogger(__name__)


class Periodic:
    """
    Inspired by https://stackoverflow.com/a/37514633

    This runs a task *right now* and then at intervals of the provided seconds.
    For long-running tasks, note that there will be `seconds` between two tasks regardless of when
    the task started.
    """

    def __init__(self, func, seconds: float):
        self.func = func
        self.seconds = seconds
        self.is_started = False
        self._task = None

    async def start(self):
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        while True:
            try:
                result = self.func()
                if inspect.isawaitable(result):
                    await result
            except Exception:
                log.exception("Periodic call failed:")
            await asyncio.sleep(self.seconds)
