# server.py
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

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            msg = conn.recv(4096).decode(FORMAT)
            if not msg:
                break
            data = json.loads(msg)
            print(f"[RECV] {data}")

            if data.get("action") == "get_movies":
                try:
                    with open(movies_file, "r", encoding="utf-8") as f:
                        movies = json.load(f)
                    conn.send(json.dumps(movies).encode(FORMAT))
                except Exception as e:
                    print(f"Lỗi đọc movies.json: {e}")
                    conn.send(json.dumps([]).encode(FORMAT))

            elif data.get("action") == "book":
                movie_id = data.get("movie_id")
                seat = data.get("seat")
                name = data.get("name")

                try:
                    with open(movies_file, "r", encoding="utf-8") as f:
                        movies = json.load(f)

                    movie = next((m for m in movies if m["id"] == movie_id), None)
                    if not movie:
                        conn.send(json.dumps({"status": "fail", "message": "Phim không tồn tại"}).encode(FORMAT))
                        return

                    if seat not in movie["ghe"]:
                        conn.send(json.dumps({"status": "fail", "message": "Ghế không hợp lệ"}).encode(FORMAT))
                        return

                    if movie["ghe"][seat] != "trong":
                        conn.send(json.dumps({"status": "fail", "message": "Ghế này đã được đặt rồi"}).encode(FORMAT))
                        return

                    movie["ghe"][seat] = name

                    with open(movies_file, "w", encoding="utf-8") as f:
                        json.dump(movies, f, indent=2, ensure_ascii=False)

                    conn.send(json.dumps({"status": "success", "message": f"Đặt vé thành công ghế {seat}"}).encode(FORMAT))

                except Exception as e:
                    print(f"Lỗi khi đặt vé: {e}")
                    conn.send(json.dumps({"status": "fail", "message": "Lỗi hệ thống"}).encode(FORMAT))

        except Exception as e:
            print(f"[ERROR] {e}")
            break

    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

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
