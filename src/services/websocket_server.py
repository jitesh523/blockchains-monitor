"""
WebSocket server for real-time updates using FastAPI and WebSockets.
"""
import logging
import os
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

app = FastAPI()

# CORS settings (allow override via env: WEBSOCKET_CORS_ORIGINS="http://localhost,http://localhost:8501")
env_origins = os.getenv("WEBSOCKET_CORS_ORIGINS")
if env_origins:
    origins = [o.strip() for o in env_origins.split(",") if o.strip()]
else:
    origins = [
        "http://localhost",
        "http://localhost:8501",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New WebSocket connection accepted")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("WebSocket disconnected")

    async def send_message(self, message: str):
        # Iterate on a copy to allow safe removal
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"WebSocket send failed, removing connection: {e}")
                try:
                    self.disconnect(connection)
                except Exception:
                    pass

# Global manager instance
manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received via WebSocket: {data}")
            await manager.send_message(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

# Function to broadcast data to all clients
async def broadcast_to_clients(data: str):
    await manager.send_message(data)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("WEBSOCKET_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


