import win32api
import win32con
import win32file
import winreg
import json
import os

SAFE_USB_FILE = "safe_usb_list.json"

def load_safe_usb():
    """Membaca daftar perangkat aman dari file JSON."""
    if os.path.exists(SAFE_USB_FILE):
        with open(SAFE_USB_FILE, "r") as f:
            return json.load(f)
    return []

def save_safe_usb(safe_list):
    """Menyimpan daftar perangkat aman ke file JSON."""
    with open(SAFE_USB_FILE, "w") as f:
        json.dump(safe_list, f, indent=4)

def list_usb_devices():
    """Mendeteksi semua perangkat USB yang terhubung."""
    drives = win32api.GetLogicalDriveStrings().split("\x00")[:-1]
    usb_drives = [drive for drive in drives if win32file.GetDriveType(drive) == win32con.DRIVE_REMOVABLE]
    return usb_drives

def set_usb_write_protect(enable: bool):
    """Mengaktifkan atau menonaktifkan USB Write Protect di Registry."""
    try:
        key_path = r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        value = 1 if enable else 0
        winreg.SetValueEx(reg_key, "WriteProtect", 0, winreg.REG_DWORD, value)
        winreg.CloseKey(reg_key)
        print(f"USB Write Protect {'diaktifkan' if enable else 'dinonaktifkan'}.")
    except Exception as e:
        print(f"Error: {e}")

def check_and_protect_usb():
    """Mengecek apakah USB terhubung ada di daftar aman, jika tidak, aktifkan proteksi tulis."""
    safe_list = load_safe_usb()
    usb_drives = list_usb_devices()

    if not usb_drives:
        print("Tidak ada perangkat USB yang terhubung.")
        return

    for drive in usb_drives:
        if drive not in safe_list:
            print(f"USB {drive} tidak ada dalam daftar aman. Mengaktifkan proteksi tulis.")
            set_usb_write_protect(True)
        else:
            print(f"USB {drive} terdaftar sebagai aman. Proteksi tulis dinonaktifkan.")
            set_usb_write_protect(False)

def add_safe_usb():
    """Menambahkan USB ke daftar aman."""
    usb_drives = list_usb_devices()
    if not usb_drives:
        print("Tidak ada perangkat USB yang terhubung.")
        return

    safe_list = load_safe_usb()
    for drive in usb_drives:
        if drive not in safe_list:
            safe_list.append(drive)
            print(f"USB {drive} ditambahkan ke daftar aman.")

    save_safe_usb(safe_list)
    print("Daftar perangkat aman diperbarui.")

if __name__ == "__main__":
    print("=== U-WaRPy Safe USB Management ===")
    print("1. Cek & Terapkan Proteksi USB")
    print("2. Tambahkan USB ke Daftar Aman")
    choice = input("Pilih opsi (1/2): ")

    if choice == "1":
        check_and_protect_usb()
    elif choice == "2":
        add_safe_usb()
    else:
        print("Pilihan tidak valid.")
