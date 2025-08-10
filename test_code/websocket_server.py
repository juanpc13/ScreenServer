import asyncio
import threading
import websockets

from frame_provider import FrameProvider, FrameProviderVideoCapture

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
                topic, content = self.message_data(message)
                match topic:
                    case "ping":
                        await websocket.send("pong")
                    case _:
                        print(f"Mensaje recibido: {message}")
                        await websocket.send(f"Echo: {message}")
        finally:
            print("Cliente desconectado")
            self.connected_clients.remove(websocket)

    def message_data(self, message):
        """
        retorna el topic y el contenido del mensaje apartir del primer ; en el array
        """
        topic = None
        content = None
        if b';' in message:
            topic, content = message.split(b';', 1)
        return topic, content

    async def broadcast(self, message):
        if self.connected_clients:
            try:
                await asyncio.gather(*(client.send(message) for client in self.connected_clients))
            except Exception as e:
                print(f"Error al enviar el mensaje: {e}")

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
            topic_prefix = "frame;".encode()
            while True:
                frame = self.frame_provider.get_frame()
                data = topic_prefix + frame
                await self.broadcast(data)
                await asyncio.sleep(1 / self.fps)

if __name__ == "__main__":
    print("Iniciando el servidor WebSocket en un hilo...")
    frame_provider = FrameProviderVideoCapture(video_source="udp://@:5000", default_image_path="logo.png")
    server = WebSocketServer(frame_provider=frame_provider)
    server.start_in_thread()
    while True:
        pass