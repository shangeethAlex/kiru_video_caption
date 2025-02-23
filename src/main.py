import cv2
import tkinter as tk
from tkinter import filedialog, ttk
import os
import numpy as np
import time
from moviepy.editor import VideoFileClip, AudioFileClip

# Ensure output folder is initialized
def get_output_folder():
    folder = output_folder_entry.get()
    if not folder:
        folder = os.path.join(os.getcwd(), "output")  # Use 'output' directory if not set
    os.makedirs(folder, exist_ok=True)  # Ensure the folder exists
    print(f"Output folder set to: {folder}")
    return folder

# Function to select video file
def select_video():
    global video_paths
    file_paths = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
    video_path_entry.delete(0, tk.END)
    video_path_entry.insert(0, ", ".join(file_paths))
    video_paths = file_paths
    print(f"Selected videos: {video_paths}")

# Function to select script file
def select_script():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    script_path_entry.delete(0, tk.END)
    script_path_entry.insert(0, file_path)
    print(f"Selected script: {file_path}")

# Function to select audio file
def select_audio():
    global audio_path
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3;*.wav;*.m4a")])
    audio_path_entry.delete(0, tk.END)
    audio_path_entry.insert(0, file_path)
    audio_path = file_path
    print(f"Selected audio: {audio_path}")

# Function to select output folder
def select_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, folder_path)
    print(f"Selected output folder: {folder_path}")

# Function to add text captions to a video
def add_text_captions(video_path, script_path, output_path,margin_offset):
    print(f"Processing video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_output_path = output_path.replace(".mp4", "_temp.mp4")
    out = cv2.VideoWriter(temp_output_path, fourcc, int(fps), (frame_width, frame_height))
    if not out.isOpened():
        print("Error: Failed to open VideoWriter.")
        return
    
    with open(script_path, 'r', encoding='utf-8') as file:
        full_caption = file.read().strip()
    
    margin = int(frame_width * 0.05)
    max_text_width = frame_width - 2 * margin
    font_scale = 1.0
    thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    frame_count = 0
    while frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            print("Warning: Missing frame, breaking loop.")
            break
        
        wrapped_lines = full_caption.split("\n")  # Ensure line-by-line captions
        text_height = len(wrapped_lines) * cv2.getTextSize("A", font, font_scale, thickness)[0][1] + 10
        text_y = frame_height - text_height - margin_offset
        
        for line in wrapped_lines:
            text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
            text_x = (frame_width - text_size[0]) // 2
            cv2.putText(frame, line, (text_x, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
            text_y += text_size[1] + 10
        
        out.write(frame)
        frame_count += 1
    
    cap.release()
    out.release()
    print(f"Captioned video saved as {temp_output_path}, Frames processed: {frame_count} out of {total_frames}")
    return temp_output_path

# Function to merge audio with video
def merge_audio_with_video(video_path, audio_path, output_path):
    print(f"Merging audio {audio_path} with video {video_path}")
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)
    
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=video.fps)
    
    print(f"Final video saved: {output_path}")
    os.remove(video_path)  # Remove intermediate video after ensuring final is saved

# Function to process multiple videos
def process_videos():
    script_path = script_path_entry.get()
    margin_offset = int(text_margin_slider.get())
    
    if not os.path.exists(script_path):
        print("Error: Invalid script file path.")
        return
    
    output_folder = get_output_folder()
    

    for video_path in video_paths:
        video_name = os.path.basename(video_path).split('.')[0]
        final_output_path = os.path.join(output_folder, f"{video_name}_final.mp4")
        
        captioned_video = add_text_captions(video_path, script_path, final_output_path, margin_offset)
        
        if os.path.exists(audio_path_entry.get()):
            merge_audio_with_video(captioned_video, audio_path_entry.get(), final_output_path)
            print(f"Final video with music saved as {final_output_path}")
        else:
            os.rename(captioned_video, final_output_path)
            print(f"Final video saved as {final_output_path}")

# UI setup
root = tk.Tk()
root.title("Video Captioning & Audio Adding Tool")

video_path_entry = tk.Entry(root, width=50)
video_path_entry.grid(row=0, column=1, padx=10, pady=5)
video_button = tk.Button(root, text="Select Videos", command=select_video)
video_button.grid(row=0, column=2, padx=10, pady=5)

script_path_entry = tk.Entry(root, width=50)
script_path_entry.grid(row=1, column=1, padx=10, pady=5)
script_button = tk.Button(root, text="Select Script", command=select_script)
script_button.grid(row=1, column=2, padx=10, pady=5)

audio_path_entry = tk.Entry(root, width=50)
audio_path_entry.grid(row=2, column=1, padx=10, pady=5)
audio_button = tk.Button(root, text="Select Audio", command=select_audio)
audio_button.grid(row=2, column=2, padx=10, pady=5)

output_folder_entry = tk.Entry(root, width=50)
output_folder_entry.grid(row=3, column=1, padx=10, pady=5)
output_folder_button = tk.Button(root, text="Select Output Folder", command=select_output_folder)
output_folder_button.grid(row=3, column=2, padx=10, pady=5)


text_margin_slider = tk.Scale(root, from_=0, to=2500, orient=tk.HORIZONTAL, label="Text Margin Offset")
text_margin_slider.set(20)
text_margin_slider.grid(row=4, column=1, columnspan=2, padx=10, pady=10)

process_button = tk.Button(root, text="Process Videos", command=process_videos)
process_button.grid(row=5, column=1, columnspan=2, padx=10, pady=10)

root.mainloop()
