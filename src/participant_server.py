from dotenv import load_dotenv

from .log import setup_logging

if True:
    setup_logging()
    load_dotenv()

import json
import logging
import os
from urllib.parse import quote

import uvloop
import websockets

from .auto_manager import AutoManager
from .finals_manager import FinalsManager
from .mock_manager import MockManager
from .models_manager import ModelsManager

TEAM_NAME = os.getenv("TEAM_NAME", "Team Name")
LOCAL_IP = os.getenv("LOCAL_IP", "0.0.0.0")
SERVER_IP = os.getenv("COMPETITION_SERVER_IP", "host.docker.internal")
SERVER_PORT = os.getenv("COMPETITION_SERVER_PORT", "8000")

# manager: FinalsManager = ModelsManager(LOCAL_IP)
# manager: FinalsManager = AutoManager(LOCAL_IP)
manager: FinalsManager = MockManager()

log = logging.getLogger(__name__)


async def server():
    index = 0
    log.info(
        f"connecting to competition server {SERVER_IP} at port {SERVER_PORT}")
    async for websocket in websockets.connect(
        quote(f"ws://{SERVER_IP}:{SERVER_PORT}/ws/{TEAM_NAME}", safe="/:"),
        max_size=2**24,
    ):

        try:
            while True:
                # should be receiving either audio bytes for asr, or done/healthcheck json
                socket_input = await websocket.recv()
                if type(socket_input) is str:
                    # handle either done or healthcheck
                    data = json.loads(socket_input)
                    if data["status"] == "done":
                        log.info("done!")
                        break
                    else:
                        await manager.send_result({"health": "ok"})
                        continue
                log.info(f"run {index}")
                # ASR
                transcript = await manager.run_asr(socket_input)
                log.info(transcript)
                # NLP
                qa_ans = await manager.run_nlp(transcript)
                log.info(qa_ans)
                query = qa_ans["target"]
                # autonomy
                try:
                    image = await manager.send_heading(qa_ans["heading"])
                except AssertionError as e:
                    # if heading is wrong, get image of scene at default heading 000
                    log.error(e, exc_info=e)
                    image = await manager.send_heading("000")
                # VLM
                vlm_results = await manager.run_vlm(image, query)
                log.info(vlm_results)
                # submit results and reset
                await manager.send_result(
                    websocket,
                    {"asr": transcript, "nlp": qa_ans, "vlm": vlm_results},
                )
                await manager.reset_cannon()
                log.info(f"done run {index}")
                index += 1
        except websockets.ConnectionClosed:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(e, exc_info=e)
        else:
            break


if __name__ == "__main__":
    uvloop.run(server())
