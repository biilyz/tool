#!/usr/bin/env python3

import usb.core
import usb.util
import array
import struct
import sys
import binascii
import time
from construct import *

dev = None

# Các ID hợp lệ của tay cầm DS4
VALID_DEVICE_IDS = [
    (0x054c, 0x05c4),
    (0x054c, 0x09cc)
]

def wait_for_device():
    global dev

    print("Đang chờ tay cầm DualShock 4...")
    while True:
        for i in VALID_DEVICE_IDS:
            dev = usb.core.find(idVendor=i[0], idProduct=i[1])
            if dev is not None:
                print(f"Đã kết nối tay cầm DS4 (Vendor: {i[0]:04x}, Product: {i[1]:04x})")
                return
        time.sleep(1)

# Lệnh HID
class HID_REQ:
    DEV_TO_HOST = usb.util.build_request_type(
        usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)
    HOST_TO_DEV = usb.util.build_request_type(
        usb.util.CTRL_OUT, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)
    GET_REPORT = 0x01
    SET_REPORT = 0x09

def hid_get_report(dev, report_id, size):
    return dev.ctrl_transfer(HID_REQ.DEV_TO_HOST, HID_REQ.GET_REPORT, report_id, 0, size + 1)[1:].tobytes()

def hid_set_report(dev, report_id, buf):
    buf = struct.pack('B', report_id) + buf
    return dev.ctrl_transfer(HID_REQ.HOST_TO_DEV, HID_REQ.SET_REPORT, (3 << 8) | report_id, 0, buf)

# Lấy dữ liệu chẩn đoán từ DS4
def dump_93_data():
    data = hid_get_report(dev, 0x93, 13)
    deviceId, targetId, numChunks, curChunk, dataLen = struct.unpack('BBBBBxxxxxxxx', data)
    if deviceId == 0xff and targetId == 0xff:
        print("Không có dữ liệu để đọc.")
        return []

    out = [data[5:5+dataLen]]

    while curChunk < numChunks - 1:
        data = hid_get_report(dev, 0x93, 13)
        deviceId, targetId, numChunks, curChunk, dataLen = struct.unpack('BBBBBxxxxxxxx', data)
        if deviceId == 0xff or targetId == 0xff:
            print("Không còn dữ liệu.")
            return out
        out.append(data[5:5+dataLen])

    return out

# Hiệu chỉnh nút cò (L2/R2)
def do_trigger_calibration():
    print("\n--- Hiệu chỉnh L2 / R2 ---")
    deviceId = 3
    hid_set_report(dev, 0x90, struct.pack('BBBB', 1, deviceId, 0, 3))

    for i in range(2):
        input("Thả L2, sau đó nhấn Enter...")
        hid_set_report(dev, 0x90, struct.pack('BBBB', 3, deviceId, 1, 1))
    for i in range(2):
        input("Giữ L2 ở giữa, sau đó nhấn Enter...")
        hid_set_report(dev, 0x90, struct.pack('BBBB', 3, deviceId, 2, 1))
    for i in range(2):
        input("Nhấn L2 hết cỡ, sau đó nhấn Enter...")
        hid_set_report(dev, 0x90, struct.pack('BBBB', 3, deviceId, 3, 1))

    for i in range(2):
        input("Thả R2, sau đó nhấn Enter...")
        hid_set_report(dev, 0x90, struct.pack('BBBB', 3, deviceId, 1, 2))
    for i in range(2):
        input("Giữ R2 ở giữa, sau đó nhấn Enter...")
        hid_set_report(dev, 0x90, struct.pack('BBBB', 3, deviceId, 2, 2))
    for i in range(2):
        input("Nhấn R2 hết cỡ, sau đó nhấn Enter...")
        hid_set_report(dev, 0x90, struct.pack('BBBB', 3, deviceId, 3, 2))

    hid_set_report(dev, 0x90, struct.pack('BBBB', 2, deviceId, 0, 3))
    print("✔ Đã hiệu chỉnh L2/R2!\n")

    print("Dữ liệu kiểm tra từ DS4:")
    data = dump_93_data()
    for i, d in enumerate(data):
        print(f"Mẫu {i}: {binascii.hexlify(d).decode('utf-8')}")

# Hiệu chỉnh vị trí trung tâm analog
def do_stick_center_calibration():
    print("\n--- Hiệu chỉnh vị trí trung tâm analog ---")
    deviceId, targetId = 1, 1

    hid_set_report(dev, 0x90, struct.pack('BBB', 1, deviceId, targetId))
    while True:
        if hid_get_report(dev, 0x91, 3) != bytes([deviceId, targetId, 1]):
            break
        if hid_get_report(dev, 0x92, 3) != bytes([deviceId, targetId, 0xff]):
            break

        choice = input("Nhấn [S] để lấy mẫu hoặc [W] để lưu (sau đó nhấn Enter): ").upper()
        if choice == "S":
            hid_set_report(dev, 0x90, struct.pack('BBB', 3, deviceId, targetId))
        elif choice == "W":
            hid_set_report(dev, 0x90, struct.pack('BBB', 2, deviceId, targetId))
            break
        else:
            print("Lựa chọn không hợp lệ!")

    print("✔ Đã hiệu chỉnh vị trí trung tâm analog!\n")

    print("Dữ liệu kiểm tra từ DS4:")
    data = dump_93_data()
    for i, d in enumerate(data):
        print(f"Mẫu {i}: {binascii.hexlify(d).decode('utf-8')}")

# Hiệu chỉnh tầm di chuyển analog
def do_stick_minmax_calibration():
    print("\n--- Hiệu chỉnh tầm di chuyển analog (min-max) ---")
    deviceId, targetId = 1, 2

    hid_set_report(dev, 0x90, struct.pack('BBB', 1, deviceId, targetId))
    assert hid_get_report(dev, 0x91, 3) == bytes([deviceId, targetId, 1])

    print("Hãy xoay cần analog khắp phạm vi hoạt động...")
    input("Khi xong, nhấn Enter để lưu hiệu chỉnh.")

    hid_set_report(dev, 0x90, struct.pack('BBB', 2, deviceId, targetId))

    print("✔ Đã hiệu chỉnh tầm di chuyển analog!\n")

    print("Dữ liệu kiểm tra từ DS4:")
    data = dump_93_data()
    for i, d in enumerate(data):
        print(f"Mẫu {i}: {binascii.hexlify(d).decode('utf-8')}")

# Hiển thị menu
def menu():
    print("\n=========== MENU ==========")
    print("1. Hiệu chỉnh vị trí trung tâm analog")
    print("2. Hiệu chỉnh phạm vi analog (min-max)")
    print("3. Hiệu chỉnh nút cò L2/R2")
    print("===========================\n")

    try:
        choice = int(input("Chọn một mục (1-3): "))
        if choice == 1:
            do_stick_center_calibration()
        elif choice == 2:
            do_stick_minmax_calibration()
        elif choice == 3:
            do_trigger_calibration()
        else:
            print("Lựa chọn không hợp lệ.")
    except ValueError:
        print("Vui lòng nhập số.")

# Chạy chính
if __name__ == "__main__":
    print("***********************************************")
    print("*  Công cụ HIỆU CHỈNH TAY CẦM DUALSHOCK 4     *")
    print("*                                             *")
    print("*  Sử dụng cẩn thận! Có thể ảnh hưởng tay cầm *")
    print("*  Tác giả:LeCuong - Phiên bản Việt hóa       *")
    print("***********************************************\n")

    wait_for_device()

    if sys.platform != 'win32' and dev.is_kernel_driver_active(0):
        try:
            dev.detach_kernel_driver(0)
        except usb.core.USBError as e:
            sys.exit("Không thể gỡ driver kernel: " + str(e))

    if dev:
        print("Tay cầm DS4 đã sẵn sàng!")

        while True:
            menu()
