import socket
import json
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font
from collections import defaultdict
import re

# --- (Phần Client class để kết nối server không đổi) ---
HEADER = 64
FORMAT = 'utf-8'
SERVER = '192.168.249.1' 
PORT = 6060
ADDR = (SERVER, PORT)
class Client:
    def __init__(self, addr):
        self.addr = addr; self.connection = None; self.connect()
    def connect(self):
        try: self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM); self.connection.connect(self.addr)
        except socket.error as e: self.connection = None; messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến server tại {self.addr[0]}:{self.addr[1]}."); exit(1)
    def request_from_server(self, data):
        if not self.connection: return {"status": "fail", "message": "Mất kết nối đến server."}
        try:
            message = json.dumps(data, ensure_ascii=False).encode(FORMAT); header = f"{len(message):<{HEADER}}".encode(FORMAT); self.connection.send(header + message)
            response_header = self.connection.recv(HEADER)
            if not response_header: return {"status": "fail", "message": "Không nhận được phản hồi từ server."}
            response_length = int(response_header.decode(FORMAT)); response_data = self.connection.recv(response_length).decode(FORMAT)
            return json.loads(response_data)
        except (ConnectionResetError, ConnectionAbortedError) as e: self.connection = None; return {"status": "fail", "message": f"Mất kết nối với server.\nLỗi: {e}"}
        except Exception as e: return {"status": "fail", "message": f"Đã có lỗi xảy ra: {e}"}

try: client = Client(ADDR)
except SystemExit: client = None

# LỚP APP CHÍNH LÀM BỘ ĐIỀU KHIỂN
class BookingApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("\u2728 Đặt Vé Xem Phim \u2728")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.name_var = tk.StringVar()
        self.sdt_var = tk.StringVar()
        self.current_movie_data = None
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (MovieSelectionPage, SeatBookingPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MovieSelectionPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if hasattr(frame, 'on_show'):
            frame.on_show()
        frame.tkraise()

    def go_to_booking_page(self, movie_data):
        self.current_movie_data = movie_data
        self.show_frame(SeatBookingPage)

    def on_closing(self):
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát?"):
            if client and client.connection: client.connection.close()
            self.destroy()




if __name__ == "__main__":
    if client:
        app = BookingApp()
        app.mainloop()