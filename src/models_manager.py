import logging
from asyncio import sleep
from base64 import b64encode
from typing import Dict, List

from src.finals_manager import FinalsManager

log = logging.getLogger(__name__)


class ModelsManager(FinalsManager):
    def __init__(self, local_ip: str):
        super().__init__()
        self.local_ip = local_ip

    async def wait_for_services(self):
        # fmt: off
        while True:
            try:
                await sleep(2)
                await self.client.get(f"http://{self.local_ip}:5001/health", timeout=None)
                await self.client.get(f"http://{self.local_ip}:5002/health", timeout=None)
                await self.client.get(f"http://{self.local_ip}:5003/health", timeout=None)
                await self.client.get(f"http://{self.local_ip}:5004/health", timeout=None)
            except Exception as e:
                log.error(e)
                continue
            break
        # fmt: on

    async def run_asr(self, audio_bytes: bytes) -> str:
        log.info("Start ASR")
        audio_str = b64encode(audio_bytes).decode("ascii")
        results = await self.async_post(
            f"http://{self.local_ip}:5001/stt", json={"instances": [{"b64": audio_str}]}
        )
        return results.json()["predictions"][0]

    async def run_nlp(self, transcript: str) -> Dict[str, str]:
        log.info("Start NLP")
        results = await self.async_post(
            f"http://{self.local_ip}:5002/extract",
            json={"instances": [{"transcript": transcript}]},
        )
        return results.json()["predictions"][0]

    async def send_heading(self, heading: str) -> bytes:
        log.info(f"Start Autonomy")
        results = await self.async_post(
            f"http://{self.local_ip}:5003/send_heading", json={"heading": heading}
        )
        # snapshot of image
        return results.content

    async def run_vlm(self, image_bytes: bytes, caption: str) -> List[int]:
        log.info("Start VLM")
        image_str = b64encode(image_bytes).decode("ascii")
        results = await self.async_post(
            f"http://{self.local_ip}:5004/identify",
            json={"instances": [{"b64": image_str, "caption": caption}]},
        )
        return results.json()["predictions"][0]

    async def reset_cannon(self):
        log.info("Reset Cannon")
        results = await self.async_post(f"http://{self.local_ip}:5003/reset_cannon")
        return results.json()
