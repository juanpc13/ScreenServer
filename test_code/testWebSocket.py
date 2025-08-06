import asyncio
import websockets

connected_clients = set()

async def echo(websocket):
    print("Cliente conectado")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Mensaje recibido: {message}")
            await websocket.send(f"Echo: {message}")
    finally:
        connected_clients.remove(websocket)

async def broadcast(message):
    if connected_clients:
        await asyncio.gather(*(client.send(f"Broadcast: {message}") for client in connected_clients))

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        print("Servidor WebSocket sencillo en ws://localhost:8765")
        # Ejemplo: enviar un mensaje a todos los clientes cada 10 segundos
        while True:
            await asyncio.sleep(10)
            await broadcast("Mensaje global desde el servidor")

if __name__ == "__main__":
    asyncio.run(main())