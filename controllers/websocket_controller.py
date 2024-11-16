from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_service import websocket_endpoint

socket_router = APIRouter()

@socket_router.websocket("/ws/sensordata")
async def get_live_data(websocket: WebSocket):
    # Establish a WebSocket connection for live sensor data.
    await websocket_endpoint(websocket)
