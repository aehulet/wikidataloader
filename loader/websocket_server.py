import asyncio
import websockets


class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def handler(self, websocket, path):
        async for message in websocket:
            print(f"Received message from client: {message}")
            await websocket.send(f"Echo: {message}")

    def run(self):
        start_server = websockets.serve(self.handler, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


# Usage
if __name__ == "__main__":
    server = WebSocketServer("localhost", 8765)
    server.run()
