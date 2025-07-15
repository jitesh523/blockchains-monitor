"""
WebSocket server for real-time updates using FastAPI and WebSockets.
"""
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

logger = logging.getLogger(__name__)

app = FastAPI()

# CORS settings
origins = [
    "http://localhost",
    "http://localhost:8501",
    # Add more allowed origins as needed
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
        for connection in self.active_connections:
            await connection.send_text(message)

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


