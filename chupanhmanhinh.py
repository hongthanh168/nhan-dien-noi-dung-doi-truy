from PIL import ImageGrab
import time
import keyboard

def capture_screen(stt):
    # Chụp màn hình và lưu vào file tạm thời
    screenshot = ImageGrab.grab()
    tenfile = f'hinhanh/screenshot{stt}.png'
    screenshot.save(tenfile)

    # # Kiểm tra hình ảnh có đồi trụy hay không
    # is_explicit = check_image_for_explicit_content('temp_screenshot.png')
    
    # if is_explicit:
    #     alert_user("Nội dung hình ảnh không phù hợp!")

# Lặp lại việc chụp màn hình sau mỗi khoảng thời gian nhất định
stt = 0
while True:
    capture_screen(stt)
    stt += 1
    time.sleep(60)  # Chụp màn hình mỗi 60 giây
    # tiếp tục chụp màn hình sau mỗi 60 giây cho đến khi người dùng nhấn ESC
    if keyboard.is_pressed('esc'):
        break
