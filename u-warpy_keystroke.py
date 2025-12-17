import win32api
import win32con
import win32file
import win32gui
import win32process
import keyboard
import json
import os
import time

SAFE_USB_FILE = "safe_usb_list.json"
SAFE_HID_FILE = "safe_hid_list.json"
SUSPICIOUS_COMMANDS = ["powershell", "cmd.exe", "taskmgr", "hostname", "new-object", "user"]
TYPING_SPEED_THRESHOLD = 0.05  # Waktu minimum antar keystroke (detik)

def load_safe_list(file_path):
    """Membaca daftar perangkat aman dari file JSON."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_safe_list(file_path, safe_list):
    """Menyimpan daftar perangkat aman ke file JSON."""
    with open(file_path, "w") as f:
        json.dump(safe_list, f, indent=4)

def list_usb_devices():
    """Mendeteksi semua perangkat USB yang terhubung."""
    drives = win32api.GetLogicalDriveStrings().split("\x00")[:-1]
    usb_drives = [drive for drive in drives if win32file.GetDriveType(drive) == win32con.DRIVE_REMOVABLE]
    return usb_drives

def detect_hid_devices():
    """Mendeteksi perangkat HID (Keyboard/Mouse) yang terhubung."""
    safe_hid_list = load_safe_list(SAFE_HID_FILE)
    hid_devices = []  # Simulasi pendeteksian perangkat HID

    # Contoh: Asumsikan kita mendeteksi 2 perangkat HID
    detected_hid = ["HID_Keyboard_01", "HID_Mouse_02"]

    for device in detected_hid:
        if device not in safe_hid_list:
            hid_devices.append(device)

    return hid_devices

def monitor_keystrokes():
    """Memantau keystroke untuk mendeteksi serangan BadUSB."""
    print("🔍 Keystroke Monitoring aktif...")
    last_time = time.time()
    buffer = ""

    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            current_time = time.time()
            time_diff = current_time - last_time
            last_time = current_time

            key = event.name.lower()
            buffer += key

            # Deteksi lonjakan kecepatan mengetik
            if time_diff < TYPING_SPEED_THRESHOLD:
                print("⚠️ Deteksi pengetikan tidak manusiawi! Memblokir input...")
                keyboard.block_key(key)
                alert("Deteksi Keystroke Injection!")

            # Deteksi perintah mencurigakan
            for command in SUSPICIOUS_COMMANDS:
                if command in buffer:
                    print(f"⚠️ Deteksi command mencurigakan: {command}! Memblokir input...")
                    keyboard.block_key(key)
                    alert(f"Deteksi command mencurigakan: {command}")

            # Reset buffer jika terlalu panjang
            if len(buffer) > 50:
                buffer = ""

def alert(message):
    """Menampilkan peringatan ke user."""
    win32gui.MessageBox(0, message, "🚨 ALERT 🚨", win32con.MB_ICONWARNING)

def main():
    print("=== U-WaRPy Keystroke Monitoring ===")
    print("1. Cek & Tambah Perangkat Aman")
    print("2. Mulai Keystroke Monitoring")
    choice = input("Pilih opsi (1/2): ")

    if choice == "1":
        # Tambahkan USB ke daftar aman
        usb_drives = list_usb_devices()
        safe_list = load_safe_list(SAFE_USB_FILE)

        for drive in usb_drives:
            if drive not in safe_list:
                safe_list.append(drive)
                print(f"USB {drive} ditambahkan ke daftar aman.")

        save_safe_list(SAFE_USB_FILE, safe_list)

        # Tambahkan HID ke daftar aman
        hid_devices = detect_hid_devices()
        safe_hid_list = load_safe_list(SAFE_HID_FILE)

        for hid in hid_devices:
            if hid not in safe_hid_list:
                safe_hid_list.append(hid)
                print(f"HID {hid} ditambahkan ke daftar aman.")

        save_safe_list(SAFE_HID_FILE, safe_hid_list)
        print("Daftar perangkat aman diperbarui.")

    elif choice == "2":
        monitor_keystrokes()

    else:
        print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()
