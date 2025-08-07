import asyncio
import threading
import websockets

class WebSocketServer:
    def __init__(self, host='0.0.0.0', port=8765, frame_provider=None, fps=20):
        self.host = host
        self.port = port
        self.fps = fps
        self.frame_provider = frame_provider
        self.connected_clients = set()

    async def echo(self, websocket):
        print("Cliente conectado")
        self.connected_clients.add(websocket)
        try:
            async for message in websocket:
                print(f"Mensaje recibido: {message}")
                await websocket.send(f"Echo: {message}")
        finally:
            print("Cliente desconectado")
            self.connected_clients.remove(websocket)

    async def broadcast_frame(self):
        if self.connected_clients and self.frame_provider:
            frame = self.frame_provider.get_frame()
            try:
                await asyncio.gather(*(client.send(frame) for client in self.connected_clients))
            except Exception as e:
                print(f"Error al enviar el frame: {e}")

    async def broadcast(self, message):
        if self.connected_clients:
            await asyncio.gather(*(client.send(f"Broadcast: {message}") for client in self.connected_clients))

    def start_server(self):
        """Inicia el servidor WebSocket en el hilo principal (bloqueante)."""
        asyncio.run(self.run())

    def start_in_thread(self):
        """Inicia el servidor WebSocket en un hilo separado."""
        thread = threading.Thread(target=self.start_server, daemon=True)
        thread.start()
        return thread

    async def run(self):
        async with websockets.serve(self.echo, self.host, self.port):
            print(f"Servidor WebSocket en ws://{self.host}:{self.port}")
            while True:
                if self.frame_provider:
                    await self.broadcast_frame()
                    await asyncio.sleep(1 / self.fps)
                else:
                    await asyncio.sleep(3)
                    await self.broadcast("Mensaje global desde el servidor")

if __name__ == "__main__":
    print("Iniciando el servidor WebSocket en un hilo...")
    server = WebSocketServer()
    server.start_in_thread()
    while True:
        pass