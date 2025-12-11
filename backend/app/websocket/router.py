import json

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from app.websocket.manager import manager
from app.websocket.events.typing import handle_typing
from app.websocket.events.presence import handle_presence_change

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str) -> None:
    became_online = await manager.connect(user_id, websocket)
    if became_online:
        await handle_presence_change(user_id, True)

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
        went_offline = manager.disconnect(user_id, websocket)
        if went_offline:
            await handle_presence_change(user_id, False)
    except Exception:
        went_offline = manager.disconnect(user_id, websocket)
        if went_offline:
            await handle_presence_change(user_id, False)
        raise