from dotenv import load_dotenv

from src.log import setup_logging

if True:
    setup_logging()
    load_dotenv()

import json
import logging
import os
from urllib.parse import quote

import uvloop
import websockets

from src.auto_manager import AutoManager
from src.finals_manager import FinalsManager
from src.mock_manager import MockManager
from src.models_manager import ModelsManager

TEAM_NAME = os.getenv("TEAM_NAME", "Team Name")
LOCAL_IP = os.getenv("LOCAL_IP", "0.0.0.0")
SERVER_IP = os.getenv("COMPETITION_SERVER_IP", "host.docker.internal")
SERVER_PORT = os.getenv("COMPETITION_SERVER_PORT", "8000")

manager: FinalsManager = ModelsManager(LOCAL_IP)
# manager: FinalsManager = AutoManager(LOCAL_IP)
# manager: FinalsManager = MockManager()

log = logging.getLogger(__name__)


async def server():
    index = 0
    log.info(f"[CONNECTING] {SERVER_IP}:{SERVER_PORT}")
    async for websocket in websockets.connect(
        quote(f"ws://{SERVER_IP}:{SERVER_PORT}/ws/{TEAM_NAME}", safe="/:"),
        max_size=2**24,
    ):

        try:
            while True:
                log.info(f"[RUN {index}]")
                # should be receiving either audio bytes for asr, or done/healthcheck json
                socket_input = await websocket.recv()
                # If its a str, its json. If its bytes, continue to ASR.
                if type(socket_input) == str:
                    # handle either done or healthcheck
                    try:
                        data = json.loads(socket_input)
                        if data["status"] == "done":
                            log.info("[DONE]")
                            break
                        else:
                            await manager.send_result({"health": "ok"})
                            continue
                    except json.JSONDecodeError:
                        log.error(f"Invalid JSON:\n{socket_input}")
                        continue

                # ASR
                transcript = await manager.run_asr(socket_input)
                log.info(f"ASR:\n{transcript}")

                # NLP
                qa_ans = await manager.run_nlp(transcript)
                log.info(f"NLP:\n{qa_ans}")
                target, heading = qa_ans["target"], qa_ans["heading"]

                # Autonomy
                image = await manager.send_heading(heading)
                log.info(f"Autonomy:\nDone")

                # VLM
                vlm_results = await manager.run_vlm(image, target)
                log.info(f"VLM:\n{vlm_results}")

                # Submit results and reset
                await manager.send_result(
                    websocket,
                    {"asr": transcript, "nlp": qa_ans, "vlm": vlm_results},
                )
                await manager.reset_cannon()
                log.info(f"[END {index}]")
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
