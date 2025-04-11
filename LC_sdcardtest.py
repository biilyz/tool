import os
import shutil
import platform
import ctypes

def parse_size(size_str):
    """Chuyển '512KB' hoặc '2MB' thành số byte"""
    size_str = size_str.strip().upper()
    if size_str.endswith("KB"):
        return int(float(size_str[:-2]) * 1024)
    elif size_str.endswith("MB"):
        return int(float(size_str[:-2]) * 1024 * 1024)
    else:
        raise ValueError("Định dạng không hợp lệ. Dùng KB hoặc MB (vd: 512KB, 1MB)")

def print_progress(current, total, prefix="📝 Đang ghi", bar_length=30):
    percent = current / total
    filled = int(bar_length * percent)
    bar = "█" * filled + "-" * (bar_length - filled)
    print(f"{prefix}: [{bar}] {percent*100:.1f}% (block {current} / {total})", end="\r")

def write_test_files(path, block_size, num_blocks):
    print("🔁 Bắt đầu ghi dữ liệu test...\n")
    for i in range(num_blocks):
        print_progress(i + 1, num_blocks)
        fname = os.path.join(path, f"block_{i:05}.bin")
        try:
            with open(fname, "wb") as f:
                f.write(bytes([i % 256]) * block_size)
        except Exception as e:
            print(f"\n❌ Lỗi khi ghi block {i}: {e}")
            break
    print_progress(num_blocks, num_blocks)
    print(f"\n✅ Ghi xong {num_blocks} block!\n")

def verify_test_files(path, block_size, num_blocks):
    print("🔍 Đang kiểm tra dữ liệu đã ghi...\n")
    for i in range(num_blocks):
        print_progress(i + 1, num_blocks, prefix="🔎 Kiểm tra")
        fname = os.path.join(path, f"block_{i:05}.bin")
        try:
            with open(fname, "rb") as f:
                data = f.read()
                if any(b != i % 256 for b in data):
                    print(f"\n❌ Dữ liệu lỗi tại block {i}")
                    break
        except FileNotFoundError:
            print(f"\n🛑 File {fname} không tồn tại.")
            break
    print_progress(num_blocks, num_blocks, prefix="🔎 Kiểm tra")
    print(f"\n✅ Kiểm tra xong {num_blocks} block!\n")

def cleanup(path):
    choice = input("🧹 Xóa dữ liệu test sau khi kiểm tra? (y/n): ").lower()
    if choice == "y":
        shutil.rmtree(path, ignore_errors=True)
        print("✅ Đã xóa dữ liệu test.")
    else:
        print("⚠️ Dữ liệu test vẫn còn trong thư mục:", path)

def get_drive_fs(path):
    """Lấy định dạng filesystem của ổ đĩa (NTFS, FAT32...)"""
    if platform.system() == "Windows":
        kernel32 = ctypes.windll.kernel32
        volume_name = ctypes.create_unicode_buffer(1024)
        fs_name = ctypes.create_unicode_buffer(1024)
        kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(path),
            volume_name,
            ctypes.sizeof(volume_name),
            None,
            None,
            None,
            fs_name,
            ctypes.sizeof(fs_name),
        )
        return fs_name.value
    else:
        import subprocess
        try:
            output = subprocess.check_output(["df", "-T", path]).decode().splitlines()
            if len(output) >= 2:
                return output[1].split()[1]  # cột type
        except Exception:
            return "unknown"

# --- MAIN ---
if __name__ == "__main__":
    print("🔰 Lê Cường – Test dung lượng ảo thẻ nhớ\n")
    drive_path = input("📥 Nhập đường dẫn thẻ nhớ (VD: E:/ hoặc /media/pi/SDCARD): ").strip()
    test_dir = os.path.join(drive_path, "test_sd")

    try:
        # Kiểm tra filesystem
        fs_type = get_drive_fs(drive_path)
        print(f"📂 File system: {fs_type}")
        if fs_type.upper() == "NTFS":
            print("🛑 Ổ đĩa đang dùng định dạng NTFS. Không phù hợp để kiểm tra kiểu này.")
            print("⚠️ Vui lòng dùng thẻ nhớ/USB với định dạng FAT32 hoặc exFAT.")
            exit()

        os.makedirs(test_dir, exist_ok=True)

        # Nhập kích thước block
        while True:
            try:
                block_size_input = input("📐 Nhập dung lượng mỗi block (VD: 1MB, 512KB): ")
                block_size = parse_size(block_size_input)
                break
            except ValueError as e:
                print("⚠️", e)

        print("\n📌 Bạn muốn nhập theo:")
        print("  1️⃣ Dung lượng tổng (GB)")
        print("  2️⃣ Số lượng block")
        choice = input("👉 Chọn (1 hoặc 2): ").strip()

        if choice == "1":
            while True:
                try:
                    size_gb = float(input("💾 Nhập dung lượng muốn test (GB): "))
                    total_bytes = size_gb * 1024 * 1024 * 1024
                    num_blocks = int(total_bytes // block_size)
                    break
                except ValueError:
                    print("⚠️ Nhập sai, vui lòng nhập số.")
        elif choice == "2":
            while True:
                try:
                    num_blocks = int(input("📦 Nhập số block muốn test: "))
                    break
                except ValueError:
                    print("⚠️ Nhập sai, vui lòng nhập số nguyên.")
        else:
            print("❌ Lựa chọn không hợp lệ.")
            exit()

        approx_gb = (block_size * num_blocks) / (1024 ** 3)
        print(f"\n🔧 Sẽ ghi {num_blocks} block x {block_size_input} ≈ {approx_gb:.2f} GB\n")

        write_test_files(test_dir, block_size, num_blocks)
        verify_test_files(test_dir, block_size, num_blocks)
        cleanup(test_dir)

    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
