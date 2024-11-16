from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException
import asyncio
from typing import List, Optional, Any, Dict
from services.pollution_service import PollutionService
from sqlalchemy.orm import Session
from config.database_config import get_db
import json
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from asyncio import Task


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class WebSocketConfig:
    update_interval: float = 2.0
    max_retries: int = 3
    retry_delay: float = 1.0

class ConnectionManager:
    def __init__(self, config: Optional[WebSocketConfig] = None):
        self.active_connections: List[WebSocket] = []
        self.config = config or WebSocketConfig()
        self.background_tasks: Dict[WebSocket, Task] = {}
        self._lock = asyncio.Lock()
        
    async def connect(self, websocket: WebSocket) -> None:
        try:
            await websocket.accept()
            async with self._lock:
                self.active_connections.append(websocket)
            logger.info(f"New connection established. Total connections: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"Failed to establish connection: {e}")
            raise
        
    async def disconnect(self, websocket: WebSocket) -> None:
        try:
            async with self._lock:
                # Handle background task cleaning
                if websocket in self.background_tasks:
                    try:
                        task = self.background_tasks[websocket]
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                    finally:

                        self.background_tasks.pop(websocket, None)
                
                # Handle connection removal
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
                    logger.info(f"Connection removed. Remaining connections: {len(self.active_connections)}")
                else:
                    logger.warning("trying to remove non-existence connection")
                    
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

            
    async def broadcast(self, message: str) -> None:
        async with self._lock:
            connections = self.active_connections.copy()
            
        disconnected = []
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(conn)

    async def start_background_task(self, websocket: WebSocket) -> None:
        task = asyncio.create_task(self._data_sender(websocket))
        async with self._lock:
            self.background_tasks[websocket] = task

    async def _data_sender(self, websocket: WebSocket) -> None:
        retry_count = 0
        
        while True:
            try:
                db = next(get_db())
                service = PollutionService(db)
                
                try:
                    data = service.fetch_live_sensor_data()
                    if data:
                        serialized_data = DataSerializer.serialize(data)
                        await websocket.send_text(json.dumps(serialized_data))
                        retry_count = 0
                finally:
                    db.close()
                
                await asyncio.sleep(self.config.update_interval)
                
            except asyncio.CancelledError:
                logger.info("Background task cancelled")
                break
            except WebSocketDisconnect:
                logger.info("Client disconnected")
                break
            except Exception as e:
                logger.error(f"Error in background task: {e}")
                retry_count += 1
                if retry_count >= self.config.max_retries:
                    logger.error("Max retry reached")
                    break
                await asyncio.sleep(self.config.retry_delay)

        try:
            await self.disconnect(websocket)
        except Exception as e:
            logger.error(f"Error during cleaning: {e}")

    def __init__(self, config: Optional[WebSocketConfig] = None):
        self.active_connections: List[WebSocket] = []
        self.config = config or WebSocketConfig()
        self.background_tasks: Dict[WebSocket, Task] = {}
        self._lock = asyncio.Lock()
        
    async def connect(self, websocket: WebSocket) -> None:
        try:
            await websocket.accept()
            async with self._lock:
                self.active_connections.append(websocket)
            logger.info(f"New connection established. Total connections: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"Failed to establish connection: {e}")
            raise
        
    async def disconnect(self, websocket: WebSocket) -> None:
        try:
            # Cancel the background task 
            if websocket in self.background_tasks:
                task = self.background_tasks[websocket]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                if websocket in self.background_tasks:
                  del self.background_tasks[websocket]
            
            async with self._lock:
                self.active_connections.remove(websocket)
            logger.info(f"Connection removed. Remaining connections: {len(self.active_connections)}")
        except ValueError:
            logger.warning("tried removing non-existence connection")
        
    async def broadcast(self, message: str) -> None:
        async with self._lock:
            connections = self.active_connections.copy()
            
        disconnected = []
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(conn)

    async def start_background_task(self, websocket: WebSocket) -> None:
        task = asyncio.create_task(self._data_sender(websocket))
        self.background_tasks[websocket] = task

    async def _data_sender(self, websocket: WebSocket) -> None:
        retry_count = 0
        
        while True:
            try:
                db = next(get_db())
                service = PollutionService(db)
                
                try:
                    data = service.fetch_live_sensor_data()
                    if data:
                        serialized_data = DataSerializer.serialize(data)
                        await websocket.send_text(json.dumps(serialized_data))
                        retry_count = 0
                finally:
                    db.close()
                
                await asyncio.sleep(self.config.update_interval)
                
            except asyncio.CancelledError:
                logger.info("Background task cancelled")
                break
            except WebSocketDisconnect:
                logger.info("Client disconnected")
                break
            except Exception as e:
                logger.error(f"Error in background task: {e}")
                retry_count += 1
                if retry_count >= self.config.max_retries:
                    logger.error("max retry reached")
                    break
                await asyncio.sleep(self.config.retry_delay)

        await self.disconnect(websocket)

class DataSerializer:
    @staticmethod
    def serialize(data: Any) -> Any:
        if isinstance(data, list):
            return [item.dict() if hasattr(item, "dict") else item.__dict__ for item in data]
        return data.dict() if hasattr(data, "dict") else data.__dict__


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    
    try:
        await manager.start_background_task(websocket)
        
        while True:
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                logger.info("Client disconnected")
                break 
            
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
    
    finally:
        if websocket in manager.active_connections:
            await manager.disconnect(websocket)
