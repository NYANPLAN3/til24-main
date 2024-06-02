import logging
from asyncio import sleep
from typing import Dict, List

from src.finals_manager import FinalsManager

log = logging.getLogger(__name__)


class MockManager(FinalsManager):
    def __init__(self):
        super().__init__()

    async def run_asr(self, audio_bytes: bytes) -> str:
        print(__name__)
        log.info("Running ASR")
        return "asr"

    async def run_nlp(self, transcript: str) -> Dict[str, str]:
        log.info("Running NLP")
        return {
            "target": "airplane",
            "heading": "180",
            "tool": "surface-to-air missiles",
        }

    async def run_vlm(self, image_bytes: bytes, caption: str) -> List[int]:
        log.info("Running VLM")
        return [0, 0, 0, 0]

    async def send_heading(self, heading: str) -> bytes:
        log.info(f"Sending cannon heading {heading}")
        await sleep(0)
        return bytes()

    async def reset_cannon(self) -> None:
        log.info("Resetting cannon to original position")
        return {}
