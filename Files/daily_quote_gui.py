import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import ctypes
import random
import os
import tkinter as tk
from tkinter import messagebox
import datetime
import subprocess
import winreg
from io import BytesIO

random.seed(datetime.date.today().toordinal())

def fetch_quote_from_api():
    try:
        res = requests.get("https://zenquotes.io/api/today")
        data = res.json()
        return data[0]['q'] + " — " + data[0]['a']
    except:
        return "Stay positive, work hard, make it happen. — Unknown"


def get_screen_resolution():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()  # For accurate scaling on high-DPI displays
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height

def should_update_today():
    today = datetime.date.today().isoformat()
    last_file = "last_updated.txt"

    # If file doesn't exist, update
    if not os.path.exists(last_file):
        return True

    with open(last_file, "r") as f:
        last_date = f.read().strip()

    return last_date != today

def save_today_date():
    with open("last_updated.txt", "w") as f:
        f.write(datetime.date.today().isoformat())


# random BG
def fetch_bg_image_url(width, height):
    day = datetime.date.today().timetuple().tm_yday
    return f"https://picsum.photos/seed/{day}/{width}/{height}?grayscale"
    # return f"https://picsum.photos/{width}/{height}?grayscale&random={day}"

def generate_wallpaper(quote):
    width, height = get_screen_resolution()

    try:
        url = fetch_bg_image_url(width, height)
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.save("debug_bg.jpg")
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.5)
    except Exception as e:
        print("❌ Error fetching Picsum image:", e)
        img = Image.new("RGB", (width, height), (30, 30, 30))
        
    # # Bg image -> solid
    # bg_path = os.path.join(os.getcwd(), "background.jpg")
    # if os.path.exists(bg_path):
    #     img = Image.open(bg_path).resize((width, height)).convert("RGB")
        
    #     # Optionally darken it for contrast
    #     enhancer = ImageEnhance.Brightness(img)
    #     img = enhancer.enhance(0.5)
    # else:
    #     img = Image.new("RGB", (width, height), (30, 30, 30))  # fallback

    draw = ImageDraw.Draw(img)

    # font
    try:
        font_path = os.path.join(os.getcwd(), "font.ttf")
        font = ImageFont.truetype(font_path, 48)
        date_font = ImageFont.truetype(font_path, 28)
    except:
        font = ImageFont.truetype("arial.ttf", 48)
        date_font = ImageFont.truetype("arial.ttf", 28)

    # quote text
    margin = 100
    lines = []
    words = quote.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if font.getbbox(test_line)[2] < width - 2 * margin:
            line = test_line
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    # Draw quote
    y = height // 2 - len(lines) * 30
    for line in lines:
        w = font.getbbox(line.strip())[2]
        draw.text(((width - w) // 2, y), line.strip(), font=font, fill="white")
        y += 55

    # date & time
    now = datetime.datetime.now().strftime("%A, %d %B %Y")
    w = date_font.getbbox(now)[2]
    draw.text(((width - w) // 2, height - 120), now, font=date_font, fill="#cccccc")

    # Save wallpaper
    out_path = os.path.join(os.getcwd(), "daily_quote_wallpaper.jpg")
    img.save(out_path)
    return out_path

def set_wallpaper(image_path):
    try:
        # Registry style
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "10")
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)

        # Set wallpaper
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)

        # Force desktop refresh
        subprocess.call(["RUNDLL32.EXE", "user32.dll,UpdatePerUserSystemParameters"])
        print("✅ Wallpaper set using Registry method.")
    except Exception as e:
        print("❌ Error:", e)

def update_wallpaper():
    quote = fetch_quote_from_api()
    wallpaper_path = generate_wallpaper(quote)
    set_wallpaper(wallpaper_path)
    messagebox.showinfo("Success", "Today's quote has been set as wallpaper!")

def create_gui():
    root = tk.Tk()
    root.title("Daily Motivational Wallpaper")
    root.geometry("400x250")
    root.configure(bg="#1e1e1e")
    root.resizable(False, False)

    label = tk.Label(root, text="Daily Quote Wallpaper", font=("Arial", 16), fg="white", bg="#1e1e1e")
    label.pack(pady=20)

    button = tk.Button(root, text="Set Today's Quote Wallpaper", command=update_wallpaper,
                       font=("Arial", 12), bg="#007acc", fg="white", padx=10, pady=5)
    button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
