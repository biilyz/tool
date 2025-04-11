# 🇻🇳 DS4 Tools - Hướng dẫn sử dụng bằng Tiếng Việt

**DS4 Tools** là công cụ giúp bạn **bật/tắt chế độ Flash** và **hiệu chỉnh tay cầm DualShock 4 (DS4)** trên Windows. Dành cho người dùng yêu thích sự đơn giản, không cần phần mềm nặng nề – chỉ cần Python và một vài script dòng lệnh!

---

## 🧰 Yêu cầu hệ thống

- Windows 10/11
- Python 3.7 trở lên
- Tay cầm DualShock 4 (cắm qua cáp USB)
- Trình điều khiển `libusb` (sử dụng Zadig)

---

## 🔧 Cài đặt nhanh

### 1. Cài Python và thư viện cần thiết

> ⚠️ Trong quá trình cài đặt Python từ [python.org](https://www.python.org/downloads/), nhớ **tick chọn "Add Python to PATH"**

Mở `CMD` hoặc `PowerShell` và chạy:

```bash
pip install construct==2.10.68
pip install pyusb==1.2.1
pip install usb==0.0.83.dev0
```

---

### 2. Cài driver libusb bằng Zadig

1. Cắm tay cầm DS4 vào máy tính
2. Tải **Zadig** tại: [https://zadig.akeo.ie](https://zadig.akeo.ie)
3. Mở Zadig > vào menu `Options > List All Devices`
4. Chọn **Wireless Controller**
5. Chọn driver `libusb-win32` và bấm **Replace Driver**

---

## 🚀 Sử dụng công cụ

Thư mục này có 2 file `.bat` dùng để thao tác với tay cầm:

### 🔁 Bật chế độ Flash (cho phép hiệu chỉnh)

Chạy file:

```
flashmirror.bat
```

### 🧪 Hiệu chỉnh tay cầm DS4

Chạy file:

```
ds4calibVN.bat
```

Sau khi hoàn tất, tay cầm đã được hiệu chỉnh chính xác.

> 🛡️ Bạn có thể chạy lại `flashmirror.bat` để đưa tay cầm về **chế độ Cấm Flash** nhằm đảm bảo an toàn khi sử dụng bình thường.

---

## 💡 Gợi ý

- Script chỉ hỗ trợ Windows.
- Cần hỗ trợ hoặc muốn đóng góp, hãy mở issue hoặc pull request trên repo này.

---



**Chúc bạn tinh chỉnh tay cầm DS4 thành công! 🎮🇻🇳**
