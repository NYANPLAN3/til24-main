import logging
from asyncio import sleep
from random import randint
from typing import Dict, List

from src.finals_manager import FinalsManager

log = logging.getLogger(__name__)


class AutoManager(FinalsManager):
    def __init__(self, local_ip: str):
        super().__init__()
        self.local_ip = local_ip

    async def wait_for_services(self):
        while True:
            try:
                await sleep(2)
                await self.client.get(f"http://{self.local_ip}:5003/health", timeout=None)
                log.info("Autonomy Healthy")
            except Exception as e:
                log.error(e)
                continue
            break

    async def run_asr(self, audio_bytes: bytes) -> str:
        log.info("Running ASR")
        return "asr"

    async def run_nlp(self, transcript: str) -> Dict[str, str]:
        log.info("Running NLP")
        return {
            "target": "airplane",
            "heading": f"{randint(1,360):03}",
            "tool": "surface-to-air missiles",
        }

    async def run_vlm(self, image_bytes: bytes, caption: str) -> List[int]:
        log.info("Running VLM")
        return [0, 0, 0, 0]

    async def send_heading(self, heading: str) -> bytes:
        assert heading.isdigit(), "The heading string contains non-digit characters"
        log.info(f"Sending cannon heading {heading}")
        results = await self.async_post(
            f"http://{self.local_ip}:5003/send_heading", json={"heading": heading}
        )
        # snapshot of image
        return results.content

    async def reset_cannon(self):
        log.info("Resetting cannon to original position")
        results = await self.async_post(f"http://{self.local_ip}:5003/reset_cannon")
        log.info(results.text)
        return results.json()
