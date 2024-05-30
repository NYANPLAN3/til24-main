import logging
from time import sleep
from typing import Dict, List

from finals_manager import FinalsManager

log = logging.getLogger(__name__)


class MockManager(FinalsManager):
    def __init__(self):
        super().__init__()

    def run_asr(self, audio_bytes: bytes) -> str:
        log.info("Running ASR")
        return "asr"

    def run_nlp(self, transcript: str) -> Dict[str, str]:
        log.info("Running NLP")
        return {
            "target": "airplane",
            "heading": "180",
            "tool": "surface-to-air missiles",
        }

    def run_vlm(self, image_bytes: bytes, caption: str) -> List[int]:
        log.info("Running VLM")
        return [0, 0, 0, 0]

    def send_heading(self, heading: str) -> bytes:
        log.info(f"Sending cannon heading {heading}")
        sleep(1)
        return bytes()

    def reset_cannon(self) -> None:
        log.info("Resetting cannon to original position")
        return {}
