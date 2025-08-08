# server.py (Đã cập nhật để xử lý nhiều ghế)
import socket
import threading
import json
import os

HEADER = 64
PORT = 6060
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_file = os.path.join(BASE_DIR, "movies.json")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

file_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            msg_length_header = conn.recv(HEADER)
            if not msg_length_header:
                break
            msg_length = int(msg_length_header.decode(FORMAT))
            msg = conn.recv(msg_length).decode(FORMAT)
            data = json.loads(msg)
            print(f"[RECV] from {addr}: {data}")

            response_data = {}

            if data.get("action") == "get_movies":
                with file_lock:
                    with open(movies_file, "r", encoding="utf-8") as f:
                        movies = json.load(f)
                response_data = movies

            # <<< THAY ĐỔI LỚN: Xử lý đặt nhiều ghế >>>
            elif data.get("action") == "book":
                movie_id = data.get("movie_id")
                seats_to_book = data.get("seats") # Nhận một danh sách ghế
                name = data.get("name")
                sdt = data.get("sdt", "") # Nhận số điện thoại

                if not seats_to_book:
                    response_data = {"status": "fail", "message": "Bạn chưa chọn ghế nào."}
                else:
                    with file_lock:
                        with open(movies_file, "r", encoding="utf-8") as f:
                            movies = json.load(f)

                        movie = next((m for m in movies if m["id"] == movie_id), None)
                        
                        can_book = True
                        error_message = ""

                        
            
            response_json = json.dumps(response_data, ensure_ascii=False).encode(FORMAT)
            response_header = f"{len(response_json):<{HEADER}}".encode(FORMAT)
            conn.send(response_header + response_json)

        except (ConnectionResetError, json.JSONDecodeError):
            print(f"[WARNING] Connection from {addr} was reset or sent invalid data.")
            break
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred with {addr}: {e}")
            break

    print(f"[DISCONNECTED] {addr} disconnected.")
    conn.close()

def start():
    server.listen()
    print(f"[STARTING] Server khởi động...")
    print(f"[LISTENING] Server đang chạy tại {SERVER}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start()