import psutil
import socket
import os
import sys
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk

def resource_path(relative_path):
    """打包成 EXE 後，確保能找到額外資源"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_network_name():
    """獲取當前連接的 Wi-Fi 或有線網路名稱"""
    if os.name == "nt":
        try:
            result = os.popen("netsh wlan show interfaces").read()
            for line in result.split("\n"):
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":")[1].strip()
        except:
            return "Unknown"
        try:
            result = os.popen("iwgetid -r").read().strip()
            return result if result else "Unknown"
        except:
            return "Unknown"
    return "Unknown"

def check_internet():
    """檢測網路是否連通"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "Connected"
    except OSError:
        return "Disconnected"

def format_speed(speed_kb):
    """將速度從 KB/s 轉換為 MB/s 或 GB/s"""
    if speed_kb >= 1024 * 1024:
        return f"{speed_kb / (1024 * 1024):.2f} GB/s"
    elif speed_kb >= 1024:
        return f"{speed_kb / 1024:.2f} MB/s"
    else:
        return f"{speed_kb:.2f} KB/s"

def get_network_speed():
    """測量當前網速（上行 / 下行）"""
    old_net = psutil.net_io_counters()
    new_net = psutil.net_io_counters()

    download_speed = (new_net.bytes_recv - old_net.bytes_recv) / 1024
    upload_speed = (new_net.bytes_sent - old_net.bytes_sent) / 1024

    return format_speed(download_speed), format_speed(upload_speed)

def update_network_status():
    """更新 GUI 上的網路資訊"""
    network_name = get_network_name()
    internet_status = check_internet()
    download_speed, upload_speed = get_network_speed()

    network_status_label.config(text=f"📶 Network: {network_name}\n🌐 Internet: {internet_status}")
    speed_label.config(text=f"⬇ {download_speed}  ⬆ {upload_speed}")

    root.after(2000, update_network_status)

def resize_event(event):
    """調整背景圖片大小，確保不變成白屏"""
    global bg_photo

    new_width = event.width
    new_height = event.height
    resized_bg = bg_image.resize((new_width, new_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(resized_bg)

    background_label.config(image=bg_photo)
    background_label.image = bg_photo
    
root = tk.Tk()
root.title("Network Monitor")
root.geometry("500x300")
root.bind("<Configure>", resize_event)

icon_path = resource_path("img/icon.ico")
root.iconbitmap(icon_path)

bg_path = resource_path("img/background.jpg")
bg_image = Image.open(bg_path)
bg_photo = ImageTk.PhotoImage(bg_image)

background_label = Label(root, image=bg_photo)
background_label.place(relwidth=1, relheight=1)

network_status_label = Label(root, text="Loading...", font=("Arial", 14), fg="white", bg="black", anchor="w", justify="left")
network_status_label.pack(pady=10, padx=10, anchor="w")

speed_label = Label(root, text="⬇ 0 KB/s  ⬆ 0 KB/s", font=("Arial", 14), fg="white", bg="black", anchor="w", justify="left")
speed_label.pack(pady=5, padx=10, anchor="w")

root.after(500, update_network_status)

root.mainloop()
