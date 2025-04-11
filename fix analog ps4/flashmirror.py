#!/usr/bin/env python3
import usb.core
import usb.util
import struct
import time
import binascii
import sys
import os


VALID_DEVICE_IDS = [
    (0x054c, 0x05c4),
    (0x054c, 0x09cc)
]

class HID_REQ:
    DEV_TO_HOST = usb.util.build_request_type(
        usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)
    HOST_TO_DEV = usb.util.build_request_type(
        usb.util.CTRL_OUT, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)
    GET_REPORT = 0x01
    SET_REPORT = 0x09

class DS4:
    def __init__(self):
        self.wait_for_device()

        if sys.platform != 'win32':
            try:
                if self.__dev.is_kernel_driver_active(0):
                    self.__dev.detach_kernel_driver(0)
            except (NotImplementedError, usb.core.USBError):
                pass

    def wait_for_device(self):
        print("Đang chờ tay cầm DualShock 4...")
        while True:
            for vendor, product in VALID_DEVICE_IDS:
                self.__dev = usb.core.find(idVendor=vendor, idProduct=product)
                if self.__dev:
                    print(f"Đã kết nối tay cầm DS4 (Vendor: {vendor:04x}, Product: {product:04x})")
                    return
            time.sleep(1)

    def hid_get_report(self, report_id, size):
        return self.__dev.ctrl_transfer(
            HID_REQ.DEV_TO_HOST, HID_REQ.GET_REPORT, report_id, 0, size + 1
        )[1:].tobytes()

    def hid_set_report(self, report_id, buf):
        buf = struct.pack('B', report_id) + buf
        return self.__dev.ctrl_transfer(
            HID_REQ.HOST_TO_DEV, HID_REQ.SET_REPORT, (3 << 8) | report_id, 0, buf
        )

class DS4Tool:
    def __init__(self, ds4):
        self.ds4 = ds4

    def xem_trang_thai_flash(self):
        self.ds4.hid_set_report(0x08, struct.pack('>BH', 0xff, 12))
        status = self.ds4.hid_get_report(0x11, 2)
        trang_thai = {
            0: " Cho Phép Flash",
            1: " Cấm Flash"
        }
        ket_qua = trang_thai.get(status[0], f"Không xác định ({status[0]})")
        print(f"→ Trạng thái flash mirror: {ket_qua}")

    def bat_flash_vinh_vien(self):
        print("→ Đang chuyển sang chế độ cho phép flash ...")
        code = binascii.unhexlify("3e717f89")
        self.ds4.hid_set_report(0xa0, struct.pack('BB', 10, 2) + code)
        self.xem_trang_thai_flash()

    def cam_flash_tam_thoi(self):
        print("→ Đang chuyển sang chế độ cấm flash ...")
        self.ds4.hid_set_report(0xa0, struct.pack('BBB', 10, 1, 0))
        self.xem_trang_thai_flash()

def main():
    ds4 = DS4()
    tool = DS4Tool(ds4)

    while True:
        print("\n==== Tùy chọn DS4 Flash Mirror ====\n")
   # Hiển thị trạng thái hiện tại
        status = tool.ds4.hid_get_report(0x11, 2)[0]
        trang_thai_text = ">>>CHO PHÉP FLASH " if status == 0 else "CẤM FLASH<<< "
        print(f"TRẠNG THÁI HIỆN TẠI:\n{trang_thai_text}\n")
        print("1. Xem trạng thái flash mirror")
        print("2. Cho phép flash")
        print("3. Cấm flash")
        print("0. Thoát")
        lua_chon = input("Chọn chức năng (0-3): ").strip()

        if lua_chon == '1':
            tool.xem_trang_thai_flash()
        elif lua_chon == '2':
            tool.bat_flash_vinh_vien()
        elif lua_chon == '3':
            tool.cam_flash_tam_thoi()
        elif lua_chon == '0':
            print("Thoát chương trình.")
            sys.exit()
        else:
            print("Lựa chọn không hợp lệ. Vui lòng thử lại.")

        input("\n-----> Nhấn ENTER để quay lại menu <-----")
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("\nĐã xảy ra lỗi:")
        print(e)
