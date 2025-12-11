import json

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from app.websocket.manager import manager
from app.websocket.events.typing import handle_typing

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str) -> None:
    await manager.connect(user_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            event = data.get("event")

            if event == "typing_start":
                await handle_typing(user_id, data, event)

            elif event == "typing_stop":
                await handle_typing(user_id, data, event)
            

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception:
        manager.disconnect(user_id, websocket)