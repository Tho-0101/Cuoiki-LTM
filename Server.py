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

# Đường dẫn tuyệt đối đến file movies.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_file = os.path.join(BASE_DIR, "movies.json")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# <<< THÊM MỚI: Tạo một Lock để bảo vệ việc đọc/ghi file movies.json
file_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            # <<< THAY ĐỔI: Đọc header trước để biết độ dài của tin nhắn
            msg_length_header = conn.recv(HEADER)
            if not msg_length_header:
                break

            msg_length = int(msg_length_header.decode(FORMAT))
            # <<< THAY ĐỔI: Đọc chính xác số byte của tin nhắn
            msg = conn.recv(msg_length).decode(FORMAT)
            
            data = json.loads(msg)
            print(f"[RECV] from {addr}: {data}")

            response_data = {} # Chuẩn bị dữ liệu để gửi lại

            if data.get("action") == "get_movies":
                try:
                    # <<< THAY ĐỔI: Sử dụng lock khi đọc file để đảm bảo an toàn
                    with file_lock:
                        with open(movies_file, "r", encoding="utf-8") as f:
                            movies = json.load(f)
                    response_data = movies
                except Exception as e:
                    print(f"Lỗi đọc movies.json: {e}")
                    response_data = []

            elif data.get("action") == "book":
                movie_id = data.get("movie_id")
                seat = data.get("seat")
                name = data.get("name")

                # <<< THAY ĐỔI: Toàn bộ quá trình đặt vé được đặt trong một lock
                with file_lock:
                    try:
                        with open(movies_file, "r", encoding="utf-8") as f:
                            movies = json.load(f)

                        movie = next((m for m in movies if m["id"] == movie_id), None)
                        if not movie:
                            response_data = {"status": "fail", "message": "Phim không tồn tại"}
                        elif seat not in movie["ghe"]:
                            response_data = {"status": "fail", "message": "Ghế không hợp lệ"}
                        elif movie["ghe"][seat] != "trong":
                            response_data = {"status": "fail", "message": "Ghế này đã được đặt rồi"}
                        else:
                            # Cập nhật thông tin
                            movie["ghe"][seat] = name
                            # Ghi lại vào file
                            with open(movies_file, "w", encoding="utf-8") as f:
                                json.dump(movies, f, indent=2, ensure_ascii=False)
                            response_data = {"status": "success", "message": f"Đặt vé thành công ghế {seat}"}

                    except Exception as e:
                        print(f"Lỗi khi đặt vé: {e}")
                        response_data = {"status": "fail", "message": "Lỗi hệ thống"}

            # <<< THAY ĐỔI: Gửi lại phản hồi cho client theo giao thức header + nội dung
            response_json = json.dumps(response_data, ensure_ascii=False).encode(FORMAT)
            response_header = f"{len(response_json):<{HEADER}}".encode(FORMAT)
            conn.send(response_header + response_json)

        except (ConnectionResetError, json.JSONDecodeError):
            # Lỗi này xảy ra khi client ngắt kết nối đột ngột hoặc gửi dữ liệu sai
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