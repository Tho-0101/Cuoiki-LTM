<<<<<<< HEAD
# server.py (Đã cập nhật để xử lý nhiều ghế)
import socket
import threading
import json
=======
>>>>>>> 946e0c098ef68491868fe180696e9251fc71fd36
import os
import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime

# Khởi tạo Flask App
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

<<<<<<< HEAD
=======
# --- Logic để tìm file movies.json ---
>>>>>>> 946e0c098ef68491868fe180696e9251fc71fd36
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_file = os.path.join(BASE_DIR, "movies.json")

# --- Các "đường dẫn" (Routes) ---

<<<<<<< HEAD
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
=======
@app.route('/')
def index():
    """Đường dẫn chính, phục vụ file giao diện HTML"""
    return render_template('index.html')

@app.route('/api/showtimes', methods=['GET'])
def get_showtimes():
    """API để lấy các suất chiếu theo ngày"""
    selected_date = request.args.get('date')
    if not selected_date:
        selected_date = datetime.today().strftime('%Y-%m-%d')

    try:
        with open(movies_file, "r", encoding="utf-8") as f:
            all_movies = json.load(f)
        
        # Lọc các phim và suất chiếu có trong ngày được chọn
        movies_on_date = []
        for movie in all_movies:
            showtimes_on_date = [st for st in movie.get("suat_chieu", []) if st["ngay"] == selected_date]
            if showtimes_on_date:
                movie_copy = movie.copy()
                movie_copy["suat_chieu"] = showtimes_on_date
                movies_on_date.append(movie_copy)
                
        return jsonify(movies_on_date)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/book', methods=['POST'])
def book_ticket():
    """API để xử lý việc đặt vé cho một suất chiếu cụ thể"""
    data = request.get_json()

    # Thêm bước kiểm tra để đảm bảo server nhận được dữ liệu hợp lệ
    if not data:
        return jsonify({"status": "fail", "message": "Yêu cầu không hợp lệ."}), 400

    movie_id = data.get("movie_id")
    show_date = data.get("date")
    show_time = data.get("time")
    seats_to_book = data.get("seats")
    name = data.get("name")
    sdt = data.get("sdt")

    if not all([movie_id, show_date, show_time, seats_to_book, name, sdt]):
        return jsonify({"status": "fail", "message": "Thiếu thông tin đặt vé."}), 400

    try:
        with open(movies_file, "r+", encoding="utf-8") as f:
            movies = json.load(f)
            movie_to_update = next((m for m in movies if m["id"] == movie_id), None)
            
            if not movie_to_update:
                return jsonify({"status": "fail", "message": "Phim không tồn tại."}), 404

            # Tìm đúng suất chiếu theo ngày và giờ
            showtime_to_update = next((st for st in movie_to_update["suat_chieu"] if st["ngay"] == show_date and st["gio"] == show_time), None)
            
            if not showtime_to_update:
                return jsonify({"status": "fail", "message": "Suất chiếu không tồn tại."}), 404

            for seat in seats_to_book:
                if seat not in showtime_to_update["ghe"]:
                    return jsonify({"status": "fail", "message": f"Ghế {seat} không hợp lệ."}), 400
                if showtime_to_update["ghe"][seat] != "trong":
                    return jsonify({"status": "fail", "message": f"Ghế {seat} đã được đặt."}), 409

            customer_info = f"{name} ({sdt})"
            for seat in seats_to_book:
                showtime_to_update["ghe"][seat] = customer_info
            
            f.seek(0)
            json.dump(movies, f, indent=2, ensure_ascii=False)
            f.truncate()

        return jsonify({"status": "success", "message": f"Đặt vé thành công!"})
    except Exception as e:
        # Ghi lại lỗi ra terminal của server để bạn có thể thấy
        print(f"Đã xảy ra lỗi nghiêm trọng: {e}") 
        return jsonify({"status": "fail", "message": f"Lỗi hệ thống: {str(e)}"}), 500

# --- Chạy server ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
>>>>>>> 946e0c098ef68491868fe180696e9251fc71fd36
