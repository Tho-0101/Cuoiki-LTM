import socket
import json
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font

FORMAT = 'utf-8'
SERVER = '10.2.159.74'  # <-- Thay bằng IP Server nếu chạy khác máy
PORT = 6060
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(ADDR)
except Exception as e:
    print(f"⚠️ Kết nối thất bại: {e}")
    exit(1)

def send(data):
    try:
        client.send(json.dumps(data).encode(FORMAT))
        raw = client.recv(4096).decode(FORMAT)
        if not raw.strip():
            raise ValueError("Dữ liệu nhận rỗng từ server")
        return json.loads(raw)
    except Exception as e:
        print(f"❌ Lỗi khi gửi/nhận: {e}")
        return {"status": "fail", "message": "Lỗi kết nối hoặc phản hồi"}

class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Client App")
        tk.Label(root, text="Giao diện client ở đây").pack(padx=20, pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()
