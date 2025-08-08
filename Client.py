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

# TRANG 1 - CHỌN PHIM
class MovieSelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#f0f2f5')
        self.controller = controller
        self.movies = []
        header_font = font.Font(family="Segoe UI", size=12, weight='bold')
        body_font = font.Font(family="Segoe UI", size=10)
        top_frame = tk.Frame(self, bg='#f0f2f5', padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        tk.Label(top_frame, text="Tên khách hàng:", bg='#f0f2f5', font=header_font).grid(row=0, column=0, sticky="w", pady=2)
        tk.Entry(top_frame, textvariable=self.controller.name_var, width=30, font=body_font).grid(row=0, column=1, sticky="w", padx=5)
        tk.Label(top_frame, text="Số điện thoại:", bg='#f0f2f5', font=header_font).grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(top_frame, textvariable=self.controller.sdt_var, width=30, font=body_font).grid(row=1, column=1, sticky="w", padx=5)
        list_frame = tk.LabelFrame(self, text="Danh sách phim", bg='#f0f2f5', padx=10, pady=10, font=header_font)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        style = ttk.Style(); style.configure("Treeview.Heading", font=header_font); style.configure("Treeview", font=body_font, rowheight=25)
        self.tree = ttk.Treeview(list_frame, columns=('ID', 'Tên', 'Giờ'), show='headings')
        self.tree.heading('ID', text='ID'); self.tree.heading('Tên', text='Tên phim'); self.tree.heading('Giờ', text='Giờ chiếu')
        self.tree.column('ID', width=50, anchor=tk.CENTER); self.tree.column('Tên', width=400); self.tree.column('Giờ', width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)
        btn_frame = tk.Frame(self, bg='#f0f2f5', pady=10)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Button(btn_frame, text="Thoát", command=self.controller.on_closing, bg='#dc3545', fg='white', font=body_font, relief=tk.FLAT).pack(side=tk.LEFT, padx=20)
        tk.Button(btn_frame, text="Xem sơ đồ ghế ➔", command=self.go_to_seats, bg='#007BFF', fg='white', font=body_font, relief=tk.FLAT).pack(side=tk.RIGHT, padx=20)
        self.load_movies()
        
    def load_movies(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        res = client.request_from_server({"action": "get_movies"})
        if isinstance(res, list) and res:
            self.movies = res
            for movie in self.movies: self.tree.insert('', tk.END, values=(movie["id"], movie["ten"], movie["gio"]))
        else:
            self.movies = [];
            if isinstance(res, dict) and "message" in res:
                 messagebox.showerror("Lỗi", res.get("message", "Không tải được danh sách phim."))

    def go_to_seats(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn phim", "Vui lòng chọn một bộ phim từ danh sách.")
            return
        name = self.controller.name_var.get().strip()
        sdt = self.controller.sdt_var.get().strip()
        if not name or not sdt:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ Tên và Số điện thoại trước khi tiếp tục.")
            return
        item_details = self.tree.item(selected_items[0])
        movie_id = item_details['values'][0]
        movie_data = next((m for m in self.movies if m['id'] == movie_id), None)
        if movie_data:
            self.controller.go_to_booking_page(movie_data)


if __name__ == "__main__":
    if client:
        app = BookingApp()
        app.mainloop()