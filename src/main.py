import cv2
import tkinter as tk
from tkinter import filedialog, ttk
import os
import numpy as np
import subprocess
import time

# Function to select video file
def select_video():
    file_paths = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
    video_path_entry.delete(0, tk.END)
    video_path_entry.insert(0, ", ".join(file_paths))
    global video_paths
    video_paths = file_paths

# Function to select script file
def select_script():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    script_path_entry.delete(0, tk.END)
    script_path_entry.insert(0, file_path)

# Function to select output folder
def select_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, folder_path)
    global output_folder
    output_folder = folder_path

# Function to wrap text into multiple lines
def wrap_text(text, font_scale, thickness, max_width, font):
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        text_size = cv2.getTextSize(test_line, font, font_scale, thickness)[0]
        if text_size[0] > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    
    lines.append(current_line)
    return lines

# Function to overlay text on video
def add_text_captions(video_path, script_path, font_choice, font_size, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}.")
        return
    
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    # Load script file and read full caption
    with open(script_path, 'r', encoding='utf-8') as file:
        full_caption = file.read().strip()
    
    margin = int(frame_width * 0.05)  # 5% margin from left and right
    max_text_width = frame_width - 2 * margin
    font_scale = float(font_size)
    thickness = 2
    font = getattr(cv2, font_choice)
    
    while True:
        wrapped_lines = wrap_text(full_caption, font_scale, thickness, max_text_width, font)
        text_height = len(wrapped_lines) * cv2.getTextSize("A", font, font_scale, thickness)[0][1] + 10
        if text_height < frame_height * 0.2:  # Ensure text fits in bottom section
            break
        font_scale -= 0.05  # Reduce font size if needed
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        text_y = frame_height - 50 - text_height  # Position text at the bottom
        
        for line in wrapped_lines:
            text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
            text_x = (frame_width - text_size[0]) // 2
            cv2.putText(frame, line, (text_x, text_y), font, 
                        font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
            text_y += text_size[1] + 10  # Move to next line
        
        out.write(frame)
        
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Output video saved as {output_path}")
    show_output_video(output_path)

# Function to process multiple videos
def process_videos():
    script_path = script_path_entry.get()
    font_choice = font_var.get()
    font_size = font_size_var.get()
    
    if not os.path.exists(script_path):
        print("Error: Invalid script file path.")
        return
    
    for video_path in video_paths:
        video_name = os.path.basename(video_path).split('.')[0]
        timestamp = int(time.time())
        output_video_path = os.path.join(output_folder, f"{video_name}_{timestamp}.mp4")
        add_text_captions(video_path, script_path, font_choice, font_size, output_video_path)

# Function to show the final output video
def show_output_video(output_path):
    if os.path.exists(output_path):
        subprocess.run(["start", output_path], shell=True)  # Open video with default player
    else:
        print("Error: Output video not found.")

# UI setup
root = tk.Tk()
root.title("Video Captioning Tool")

video_path_entry = tk.Entry(root, width=50)
video_path_entry.grid(row=0, column=1, padx=10, pady=5)
video_button = tk.Button(root, text="Select Videos", command=select_video)
video_button.grid(row=0, column=2, padx=10, pady=5)

script_path_entry = tk.Entry(root, width=50)
script_path_entry.grid(row=1, column=1, padx=10, pady=5)
script_button = tk.Button(root, text="Select Script", command=select_script)
script_button.grid(row=1, column=2, padx=10, pady=5)

output_folder_entry = tk.Entry(root, width=50)
output_folder_entry.grid(row=2, column=1, padx=10, pady=5)
output_folder_button = tk.Button(root, text="Select Output Folder", command=select_output_folder)
output_folder_button.grid(row=2, column=2, padx=10, pady=5)

font_var = tk.StringVar(value="FONT_HERSHEY_SIMPLEX")
font_label = tk.Label(root, text="Select Font:")
font_label.grid(row=3, column=0, padx=10, pady=5)
font_dropdown = ttk.Combobox(root, textvariable=font_var, values=[
    "FONT_HERSHEY_SIMPLEX", "FONT_HERSHEY_PLAIN", "FONT_HERSHEY_DUPLEX", "FONT_HERSHEY_COMPLEX",
    "FONT_HERSHEY_TRIPLEX", "FONT_HERSHEY_COMPLEX_SMALL", "FONT_HERSHEY_SCRIPT_SIMPLEX", "FONT_HERSHEY_SCRIPT_COMPLEX"
])
font_dropdown.grid(row=3, column=1, padx=10, pady=5)
font_dropdown.current(0)

font_size_var = tk.StringVar(value="1.0")
font_size_label = tk.Label(root, text="Font Size:")
font_size_label.grid(row=4, column=0, padx=10, pady=5)
font_size_entry = tk.Entry(root, textvariable=font_size_var, width=10)
font_size_entry.grid(row=4, column=1, padx=10, pady=5)

process_button = tk.Button(root, text="Process Videos", command=process_videos)
process_button.grid(row=5, column=1, columnspan=2, padx=10, pady=10)

root.mainloop()
