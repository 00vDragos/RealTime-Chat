from datetime import datetime
from typing import Dict, List
from fastapi import WebSocket
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.messages import Message


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, user_id: str, message: dict) -> None:
        if user_id in self.active_connections:
            for conn in self.active_connections[user_id]:
                await conn.send_json(message)
            msg_data = message.get("message")
            if msg_data and "id" in msg_data:
                msg_id = msg_data["id"]

                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(Message).where(Message.id == msg_id))
                    msg = result.scalar_one_or_none()
                    if msg:
                        delivered_map = msg.delivered_at or {}
                        delivered_map[user_id] = datetime.utcnow().isoformat()
                        msg.delivered_at = delivered_map
                        await db.commit()


    async def broadcast(self, user_ids: list[str], message: dict) -> None:
        for uid in user_ids:
            await self.send_personal_message(uid, message)

manager = ConnectionManager()
