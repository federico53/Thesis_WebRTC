import asyncio
import websockets
import json

connected_clients = set()

async def handler(websocket, path):
    # Aggiunge il nuovo client connesso alla lista dei client
    connected_clients.add(websocket)
    print('Un nuovo client si è connesso.')

    try:
        # Invia un messaggio di benvenuto al nuovo client
        await websocket.send(json.dumps({'message': 'Benvenuto! Sei connesso al server WebSocket.'}))

        async for message in websocket:
            print('Messaggio ricevuto:', message)

            # Deserializza il messaggio JSON
            try:
                received_data = json.loads(message)
            except json.JSONDecodeError as error:
                print('Errore di parsing JSON:', error)
                continue

            print('Dati ricevuti:', received_data)

            # Inoltra il messaggio a tutti gli altri client connessi
            for client in connected_clients:
                if client != websocket and client.open:
                    print('Inoltro messaggio a un client.', json.dumps(received_data))
                    await client.send(json.dumps(received_data))

    finally:
        # Rimuove il client disconnesso dalla lista dei client
        connected_clients.remove(websocket)
        print('Un client si è disconnesso.')

async def main():
    server = await websockets.serve(handler, "192.168.56.212", 8080)
    print('Server WebSocket in ascolto su ws://192.168.56.212:8080')
    await server.wait_closed()

asyncio.run(main())
