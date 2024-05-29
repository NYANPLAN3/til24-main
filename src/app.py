"""Main app."""

from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging

from fastapi import FastAPI

__all__ = ["create_app"]
log = logging.getLogger(__name__)


def create_app():
    """App factory.

    Creating the app within a function prevents mishaps if using multiprocessing.
    """
    app = FastAPI()

    @app.get("/hello")
    async def hello():
        """Returns a greeting.

        Returns:
            dict: A greeting message.
        """
        log.warn("zzz... 1 more second...")
        await asyncio.sleep(1)
        log.info("...zzz... oh wha...?!")
        return {"message": "Hello, World!"}

    return app
