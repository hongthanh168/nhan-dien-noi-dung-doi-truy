# pip install -r requirements.txt
import tkinter as tk
from tkinter import messagebox
import hashlib
import os
import psutil
import threading
import sched
import time
from PIL import ImageGrab, Image
from ultralytics import YOLO
import supervision as sv
import numpy as np
import pystray
from pystray import MenuItem as item

# Định nghĩa các giá trị mặc định
IOU_THRESHOLD = 0.3
CONFIDENCE_THRESHOLD = 0.2
pretrained_path = "erax_nsfw_yolo11m.pt"
screenshot_interval = 30  # Mặc định là 30 giây
password_file = "user.txt"
scheduler = sched.scheduler(time.time, time.sleep)

# Hàm mã hóa mật khẩu bằng MD5
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Hàm kiểm tra mật khẩu
def check_password(input_password):
    if not os.path.exists(password_file):
        messagebox.showerror("Error", "File user.txt không tồn tại.")
        return False
    
    with open(password_file, 'r') as file:
        stored_password = file.read().strip()

    hashed_input = hash_password(input_password)
    return hashed_input == stored_password

# Hàm đóng các trình duyệt
def close_browsers():
    browser_names = ["chrome", "firefox", "msedge", "opera", "brave", "safari"]
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and any(browser in proc.info['name'].lower() for browser in browser_names):
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# Hàm kiểm tra hình ảnh đồi trụy
def check_nsfw_image(image):
    model = YOLO(pretrained_path)
    results = model(image, conf=CONFIDENCE_THRESHOLD, iou=IOU_THRESHOLD)
    for result in results:
        selected_classes = [0, 2, 3, 4, 5]
        detections = sv.Detections.from_ultralytics(result)
        detections = detections[np.isin(detections.class_id, selected_classes)]
        if len(detections) > 0:
            return True
    return False

# Hàm chụp màn hình
def capture_screen():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    return "screenshot.png"

# Hàm thực hiện chụp màn hình và kiểm tra hình ảnh
def take_screenshot_and_check():
    screenshot_path = capture_screen()
    if check_nsfw_image(screenshot_path):
        messagebox.showwarning("Cảnh báo", "Bạn không được xem hình ảnh đồi trụy!")
        close_browsers()
    scheduler.enter(screenshot_interval, 1, take_screenshot_and_check)

# Hàm khởi chạy chương trình kiểm tra
def start_monitoring():
    scheduler.enter(screenshot_interval, 1, take_screenshot_and_check)
    threading.Thread(target=scheduler.run, daemon=True).start()

# Hàm để ẩn cửa sổ Tkinter
def hide_window():
    root.withdraw()

# Hàm khôi phục cửa sổ Tkinter
def show_window():
    root.deiconify()

# Hàm thoát chương trình từ system tray
def quit_program(icon, item):
    icon.stop()
    root.quit()

# Hàm tạo icon trên system tray
def setup_tray_icon():
    image = Image.open("icon.png")  # Đường dẫn tới file icon
    menu = (item('Show', lambda: show_window()), item('Quit', quit_program))
    icon = pystray.Icon("name", image, "NSFW Checker", menu)
    threading.Thread(target=icon.run, daemon=True).start()

# Giao diện đăng nhập
def login():
    input_password = password_entry.get()
    if check_password(input_password):
        root.withdraw()  # Ẩn cửa sổ đăng nhập
        start_app()  # Bắt đầu chương trình chính
    else:
        messagebox.showerror("Lỗi", "Mật khẩu không đúng!")

# Giao diện chính
def start_app():
    app = tk.Tk()
    app.title("Chương trình kiểm tra hình ảnh")

    # Label hướng dẫn
    label = tk.Label(app, text="Thiết lập khoảng thời gian chụp màn hình (giây):")
    label.pack(pady=10)

    # Menu chọn thời gian chụp màn hình
    def set_interval(value):
        global screenshot_interval
        screenshot_interval = int(value)

    interval_var = tk.StringVar(app)
    interval_var.set("30")  # Mặc định là 30 giây
    interval_menu = tk.OptionMenu(app, interval_var, "10", "20", "30", "60", command=set_interval)
    interval_menu.pack(pady=10)

    # Nút bắt đầu
    def on_start():
        start_monitoring()
        hide_window()  # Ẩn cửa sổ chính khi bấm "Bắt đầu kiểm tra"
        setup_tray_icon()  # Tạo icon trên system tray

    start_button = tk.Button(app, text="Bắt đầu kiểm tra", command=on_start)
    start_button.pack(pady=20)

    app.mainloop()

# Giao diện đăng nhập
root = tk.Tk()
root.title("Đăng nhập")

label = tk.Label(root, text="Nhập mật khẩu:")
label.pack(pady=10)

password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=10)

login_button = tk.Button(root, text="Đăng nhập", command=login)
login_button.pack(pady=10)

root.mainloop()
