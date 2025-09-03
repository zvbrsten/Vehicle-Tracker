import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2
import tempfile
import threading
import time
import sys

from utils.ocr import extract_text_and_dob
from utils.age_check import is_above_18
from utils.blink_detect import detect_blink
from utils.face_compare import compare_faces
from utils.spoof_detect import detect_screen_or_print
# Globals
adhar_path = None
selfie_path = os.path.join(tempfile.gettempdir(), "selfie.jpg")
dob = None
cap = None

# GUI Setup
root = tk.Tk()
root.title("Aadhaar + Liveness + Face Verification")
root.geometry("650x700")
root.configure(bg="#f0f0f0")

header = tk.Label(root, text="AADHAR VERIFICATION PORTAL BY YASH SHARMA", font=("Arial", 18, "bold"), fg="#003366", bg="#f0f0f0")
header.pack(pady=20)

status_label = tk.Label(root, text="Status: Waiting", fg="#006600", font=("Arial", 13, "bold"), bg="#f0f0f0")
status_label.pack(pady=10)

aadhaar_image_label = tk.Label(root, bg="#f0f0f0")
aadhaar_image_label.pack(pady=10)

camera_label = tk.Label(root, bg="#f0f0f0")
camera_label.pack(pady=10)

# Aadhaar Upload
def upload_aadhaar():
    global adhar_path, dob
    adhar_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not adhar_path:
        return

    upload_btn.config(state="disabled")

    image = Image.open(adhar_path).resize((200, 200))
    photo = ImageTk.PhotoImage(image)
    aadhaar_image_label.config(image=photo)
    aadhaar_image_label.image = photo

    status_label.config(text="Extracting DOB from Aadhaar...")
    root.update()

    text, dob = extract_text_and_dob(adhar_path)
    if not dob:
        messagebox.showerror("Error", "DOB not found in Aadhaar.")
        return

    if not is_above_18(dob):
        status_label.config(text=f"DOB: {dob} — User is underage.")
        return

    status_label.config(text=f"DOB: {dob} — Age verified (18+)")
    root.after(1000, blink_detection_gui)

# Blink Detection
def blink_detection_gui():
    global cap
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Cannot open webcam")
        return

    required_blinks = 5
    blink_count = 0
    last_blink_time = 0
    cooldown = 1.2

    status_label.config(text=f"Blinks detected: 0/{required_blinks}")
    camera_label.config(text="")

    def update_frame():
        nonlocal blink_count, last_blink_time

        ret, frame = cap.read()
        if not ret:
            status_label.config(text="Camera error")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)

        current_time = time.time()
        if detect_blink(frame):
            if current_time - last_blink_time > cooldown:
                blink_count += 1
                last_blink_time = current_time
                status_label.config(text=f"Blinks detected: {blink_count}/{required_blinks}")
                root.update_idletasks()

        if blink_count < required_blinks:
            root.after(30, update_frame)
        else:
            cap.release()
            camera_label.config(image='')
            status_label.config(text="Liveness check complete. Capturing selfie... Make sure face is in the centre and is well lit")
            root.after(1000, lambda: threading.Thread(target=capture_selfie).start())

    update_frame()

# Capture Selfie Automatically
def capture_selfie():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Could not open webcam for selfie.")
        return

    status_label.config(text="Capturing selfie... Please hold still.")
    root.update()

    def grab_frame():
        # Warm-up frames
        for _ in range(10):  # read few dummy frames
            cap.read()
            time.sleep(0.1)

        ret, frame = cap.read()
        if ret and frame is not None:
            cv2.imwrite(selfie_path, frame)
            cap.release()

            selfie_img = Image.open(selfie_path).resize((200, 200))
            selfie_photo = ImageTk.PhotoImage(selfie_img)
            camera_label.config(image=selfie_photo)
            camera_label.image = selfie_photo
            status_label.config(text="Selfie captured.")
            root.after(1500, run_final_verification)
        else:
            cap.release()
            messagebox.showerror("Capture Error", "Could not read frame from camera.")

    root.after(1000, grab_frame)


# Restart app
def restart_app():
    python = sys.executable
    os.execl(python, python, *sys.argv)

# Verification
def run_final_verification():
    def show_restart():
        tk.Button(root, text="Restart", font=("Arial", 12, "bold"), bg="#0066cc", fg="white", command=restart_app).pack(pady=15)

    try:
        img = Image.open(selfie_path)
        is_spoof, lap_var, color_std = detect_screen_or_print(img)
        if is_spoof:
            messagebox.showerror("Spoof Detected", f"Laplacian: {lap_var:.2f}, Color STD: {color_std:.2f}")
            status_label.config(text="Verification Failed: Spoof Detected")
            root.after(1000, show_restart)
            return

        similarity = compare_faces(adhar_path, selfie_path)
        if similarity > 0.6:
            messagebox.showinfo("Success", f"Similarity: {similarity:.4f}\nIdentity verified.")
            status_label.config(text="Verification Passed")
        else:
            messagebox.showwarning("Mismatch", f"Similarity: {similarity:.4f}\nFace mismatch.")
            status_label.config(text="Verification Failed")

        root.after(1000, show_restart)

    except Exception as e:
        messagebox.showerror("Error", str(e))
        root.after(1000, show_restart)

# Upload Button
upload_btn = tk.Button(root, text="Upload Aadhaar", font=("Arial", 13, "bold"), bg="#004080", fg="white", command=upload_aadhaar)
upload_btn.pack(pady=20)

root.mainloop()
