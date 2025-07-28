import socket
import threading
import json

from chat.reply_engine import generate_reply  # AI chatbot logic

from wsproto import WSConnection
from wsproto.connection import SERVER
from wsproto.events import (
    AcceptConnection,
    Request,
    TextMessage,
    CloseConnection
)

# Set the host and port for the server
HOST = '127.0.0.1'
PORT = 8765

# Send data to the client socket
def send_to_client(socket, data):
    try:
        socket.send(data)
    except Exception as e:
        print("Failed to send data:", e)

# Handle WebSocket handshake
def handle_handshake(ws, client_socket):
    try:
        handshake_data = client_socket.recv(1024)
        ws.receive_data(handshake_data)

        for event in ws.events():
            if isinstance(event, Request):
                accept_bytes = ws.send(AcceptConnection())
                send_to_client(client_socket, accept_bytes)
                return True
    except Exception as e:
        print("Handshake error:", e)
    return False

# Process a WebSocket event
def process_event(event, ws, client_socket):
    if isinstance(event, TextMessage):
        try:
            # Parse incoming JSON and extract client message
            parsed = json.loads(event.data)
            user_msg = parsed.get("message", "")

            # Call generate_reply function to generate answer for client message
            reply = generate_reply(user_msg)
            reply_json = json.dumps(reply)
        except Exception:
            reply_json = json.dumps({"error": "Invalid message format"})

        # Send chatbot reply back to client
        reply_bytes = ws.send(TextMessage(data=reply_json))
        send_to_client(client_socket, reply_bytes)

    elif isinstance(event, CloseConnection):
        print("Client requested to close the connection.")
        return False  # Stop the message loop

    return True  # Continue the message loop

# Handle client connection
def handle_client(client_socket):
    ws = WSConnection(SERVER)

    if not handle_handshake(ws, client_socket):
        client_socket.close()
        return

    try:
        while True:
            raw_data = client_socket.recv(2048)
            if not raw_data:
                break

            ws.receive_data(raw_data)
            for event in ws.events():
                if not process_event(event, ws, client_socket):
                    return
    except Exception as e:
        print("Error during client communication:", e)
    finally:
        client_socket.close()
        print("Connection closed.")

# Start the WebSocket server and listen for new connections
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"WebSocket server running at ws://{HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

# Run the server
if __name__ == "__main__":
    start_server()
