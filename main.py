# import tkinter as tk
# from tkinter import filedialog, messagebox
# from PIL import Image, ImageTk
# import os
# import cv2
# import tempfile
# import threading
# import time
# import sys

# from utils.ocr import extract_text_and_dob
# from utils.age_check import is_above_18
# from utils.blink_detect import detect_blink
# from utils.face_compare import compare_faces
# from utils.spoof_detect import detect_screen_or_print
# # Globals
# adhar_path = None
# selfie_path = os.path.join(tempfile.gettempdir(), "selfie.jpg")
# dob = None
# cap = None

# # GUI Setup
# root = tk.Tk()
# root.title("Aadhaar + Liveness + Face Verification")
# root.geometry("650x700")
# root.configure(bg="#f0f0f0")

# header = tk.Label(root, text="AADHAR VERIFICATION PORTAL BY YASH SHARMA", font=("Arial", 18, "bold"), fg="#003366", bg="#f0f0f0")
# header.pack(pady=20)

# status_label = tk.Label(root, text="Status: Waiting", fg="#006600", font=("Arial", 13, "bold"), bg="#f0f0f0")
# status_label.pack(pady=10)

# aadhaar_image_label = tk.Label(root, bg="#f0f0f0")
# aadhaar_image_label.pack(pady=10)

# camera_label = tk.Label(root, bg="#f0f0f0")
# camera_label.pack(pady=10)

# # Aadhaar Upload
# def upload_aadhaar():
#     global adhar_path, dob
#     adhar_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
#     if not adhar_path:
#         return

#     upload_btn.config(state="disabled")

#     image = Image.open(adhar_path).resize((200, 200))
#     photo = ImageTk.PhotoImage(image)
#     aadhaar_image_label.config(image=photo)
#     aadhaar_image_label.image = photo

#     status_label.config(text="Extracting DOB from Aadhaar...")
#     root.update()

#     text, dob = extract_text_and_dob(adhar_path)
#     if not dob:
#         messagebox.showerror("Error", "DOB not found in Aadhaar.")
#         return

#     if not is_above_18(dob):
#         status_label.config(text=f"DOB: {dob} — User is underage.")
#         return

#     status_label.config(text=f"DOB: {dob} — Age verified (18+)")
#     root.after(1000, blink_detection_gui)

# # Blink Detection
# def blink_detection_gui():
#     global cap
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         messagebox.showerror("Camera Error", "Cannot open webcam")
#         return

#     required_blinks = 5
#     blink_count = 0
#     last_blink_time = 0
#     cooldown = 1.2

#     status_label.config(text=f"Blinks detected: 0/{required_blinks}")
#     camera_label.config(text="")

#     def update_frame():
#         nonlocal blink_count, last_blink_time

#         ret, frame = cap.read()
#         if not ret:
#             status_label.config(text="Camera error")
#             return

#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         img_pil = Image.fromarray(frame_rgb)
#         imgtk = ImageTk.PhotoImage(image=img_pil)
#         camera_label.imgtk = imgtk
#         camera_label.configure(image=imgtk)

#         current_time = time.time()
#         if detect_blink(frame):
#             if current_time - last_blink_time > cooldown:
#                 blink_count += 1
#                 last_blink_time = current_time
#                 status_label.config(text=f"Blinks detected: {blink_count}/{required_blinks}")
#                 root.update_idletasks()

#         if blink_count < required_blinks:
#             root.after(30, update_frame)
#         else:
#             cap.release()
#             camera_label.config(image='')
#             status_label.config(text="Liveness check complete. Capturing selfie... Make sure face is in the centre and is well lit")
#             root.after(1000, lambda: threading.Thread(target=capture_selfie).start())

#     update_frame()

# # Capture Selfie Automatically
# def capture_selfie():
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         messagebox.showerror("Camera Error", "Could not open webcam for selfie.")
#         return

#     status_label.config(text="Capturing selfie... Please hold still.")
#     root.update()

#     def grab_frame():
#         # Warm-up frames
#         for _ in range(10):  # read few dummy frames
#             cap.read()
#             time.sleep(0.1)

#         ret, frame = cap.read()
#         if ret and frame is not None:
#             cv2.imwrite(selfie_path, frame)
#             cap.release()

#             selfie_img = Image.open(selfie_path).resize((200, 200))
#             selfie_photo = ImageTk.PhotoImage(selfie_img)
#             camera_label.config(image=selfie_photo)
#             camera_label.image = selfie_photo
#             status_label.config(text="Selfie captured.")
#             root.after(1500, run_final_verification)
#         else:
#             cap.release()
#             messagebox.showerror("Capture Error", "Could not read frame from camera.")

#     root.after(1000, grab_frame)


# # Restart app
# def restart_app():
#     python = sys.executable
#     os.execl(python, python, *sys.argv)

# # Verification
# def run_final_verification():
#     def show_restart():
#         tk.Button(root, text="Restart", font=("Arial", 12, "bold"), bg="#0066cc", fg="white", command=restart_app).pack(pady=15)

#     try:
#         img = Image.open(selfie_path)
#         is_spoof, lap_var, color_std = detect_screen_or_print(img)
#         if is_spoof:
#             messagebox.showerror("Spoof Detected", f"Laplacian: {lap_var:.2f}, Color STD: {color_std:.2f}")
#             status_label.config(text="Verification Failed: Spoof Detected")
#             root.after(1000, show_restart)
#             return

#         similarity = compare_faces(adhar_path, selfie_path)
#         if similarity > 0.6:
#             messagebox.showinfo("Success", f"Similarity: {similarity:.4f}\nIdentity verified.")
#             status_label.config(text="Verification Passed")
#         else:
#             messagebox.showwarning("Mismatch", f"Similarity: {similarity:.4f}\nFace mismatch.")
#             status_label.config(text="Verification Failed")

#         root.after(1000, show_restart)

#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         root.after(1000, show_restart)

# # Upload Button
# upload_btn = tk.Button(root, text="Upload Aadhaar", font=("Arial", 13, "bold"), bg="#004080", fg="white", command=upload_aadhaar)
# upload_btn.pack(pady=20)

# root.mainloop()

import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import os

# Initialize session state
if 'last_timestamps' not in st.session_state:
    st.session_state.last_timestamps = {
        'MTW': None,
        'Car': None,
        '3W': None,
        'Buses': None,
        'Cycles': None
    }

if 'vehicle_counts' not in st.session_state:
    st.session_state.vehicle_counts = {
        'MTW': 0,
        'Car': 0,
        '3W': 0,
        'Buses': 0,
        'Cycles': 0
    }

def log_to_csv(school_name, vehicle_type, timestamp, time_diff, count):
    """Log vehicle data to CSV file"""
    filename = f"{school_name.replace(' ', '_')}_vehicle_log.csv"
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.isfile(filename)
    
    # Prepare data
    data = {
        'School_Name': school_name,
        'Vehicle_Type': vehicle_type,
        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'Time_Since_Last_Press': time_diff,
        'Total_Count': count
    }
    
    # Write to CSV
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['School_Name', 'Vehicle_Type', 'Timestamp', 'Time_Since_Last_Press', 'Total_Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)

def format_time_diff(time_diff):
    """Format time difference in readable format"""
    if time_diff is None:
        return "First press"
    
    total_seconds = int(time_diff.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

# Streamlit App
st.title("🚗 Vehicle Tracking Timer")
st.markdown("---")

# School name input
school_name = st.text_input("Enter School Name:", placeholder="e.g., ABC Public School")

if not school_name:
    st.warning("Please enter a school name to continue.")
    st.stop()

# Display current counts
st.subheader("📊 Current Vehicle Counts")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("MTW (Motorcycles)", st.session_state.vehicle_counts['MTW'])
with col2:
    st.metric("Cars", st.session_state.vehicle_counts['Car'])
with col3:
    st.metric("3W (Auto)", st.session_state.vehicle_counts['3W'])
with col4:
    st.metric("Buses", st.session_state.vehicle_counts['Buses'])
with col5:
    st.metric("Cycles", st.session_state.vehicle_counts['Cycles'])

st.markdown("---")

# Timer buttons
st.subheader("⏱️ Vehicle Timer Buttons")

# Create buttons in columns for better layout
col1, col2, col3, col4, col5 = st.columns(5)

vehicle_types = ['MTW', 'Car', '3W', 'Buses', 'Cycles']
button_colors = ['🏍️', '🚗', '🛺', '🚌', '🚲']

for i, (vehicle_type, emoji) in enumerate(zip(vehicle_types, button_colors)):
    with [col1, col2, col3, col4, col5][i]:
        if st.button(f"{emoji} {vehicle_type}", key=vehicle_type, use_container_width=True):
            current_time = datetime.now()
            last_time = st.session_state.last_timestamps[vehicle_type]
            
            # Calculate time difference
            time_diff = None
            if last_time:
                time_diff = current_time - last_time
            
            # Update count
            st.session_state.vehicle_counts[vehicle_type] += 1
            
            # Log to CSV
            log_to_csv(
                school_name, 
                vehicle_type, 
                current_time, 
                format_time_diff(time_diff), 
                st.session_state.vehicle_counts[vehicle_type]
            )
            
            # Update last timestamp
            st.session_state.last_timestamps[vehicle_type] = current_time
            
            # Show success message
            time_diff_str = format_time_diff(time_diff)
            st.success(f"✅ {vehicle_type} logged! Time since last press: {time_diff_str}")
            st.rerun()

st.markdown("---")

# Display last press times
st.subheader("🕐 Last Press Times")
for vehicle_type in vehicle_types:
    last_time = st.session_state.last_timestamps[vehicle_type]
    if last_time:
        st.write(f"**{vehicle_type}**: {last_time.strftime('%H:%M:%S')} ({format_time_diff(datetime.now() - last_time)} ago)")
    else:
        st.write(f"**{vehicle_type}**: Not pressed yet")

# Reset functionality
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🔄 Reset All Counters", type="secondary", use_container_width=True):
        st.session_state.last_timestamps = {key: None for key in st.session_state.last_timestamps}
        st.session_state.vehicle_counts = {key: 0 for key in st.session_state.vehicle_counts}
        st.success("All counters have been reset!")
        st.rerun()

# Display CSV file info
if school_name:
    filename = f"{school_name.replace(' ', '_')}_vehicle_log.csv"
    if os.path.isfile(filename):
        st.markdown("---")
        st.subheader("📄 Log File Information")
        
        try:
            df = pd.read_csv(filename)
            st.write(f"**File**: `{filename}`")
            st.write(f"**Total entries**: {len(df)}")
            
            # Show recent entries
            if len(df) > 0:
                st.write("**Recent entries**:")
                st.dataframe(df.tail(5), use_container_width=True)
                
                # Download button
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

# Instructions
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    1. **Enter School Name**: Type the name of your school in the input field
    2. **Press Vehicle Buttons**: Click on the appropriate vehicle type button when a vehicle passes
    3. **View Logs**: The app automatically logs each button press with:
       - Timestamp of the press
       - Time elapsed since the last press of the same vehicle type
       - Running count of vehicles per type
    4. **Download Data**: You can download the CSV file containing all logged data
    5. **Reset Counters**: Use the reset button to clear all counters and start fresh
    
    **Vehicle Types:**
    - **MTW**: Motorcycles/Two-wheelers 🏍️
    - **Car**: Cars 🚗
    - **3W**: Three-wheelers/Auto rickshaws 🛺
    - **Buses**: Buses 🚌
    - **Cycles**: Bicycles 🚲
    """)
