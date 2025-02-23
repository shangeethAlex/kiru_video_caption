import tkinter as tk
from tkinter import filedialog

def select_video(video_path_entry):
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
    video_path_entry.delete(0, tk.END)
    video_path_entry.insert(0, file_path)

def select_script(script_path_entry):
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    script_path_entry.delete(0, tk.END)
    script_path_entry.insert(0, file_path)
