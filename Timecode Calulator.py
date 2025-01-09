import subprocess
import sys

# Ensure ttkbootstrap is installed
def ensure_ttkbootstrap_installed():
    try:
        import ttkbootstrap
    except ImportError:
        print("ttkbootstrap not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ttkbootstrap"])

ensure_ttkbootstrap_installed()

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import re
from tkinter import messagebox

def timecode_to_frames(timecode, fps):
    pattern = r"(\d+):(\d+):(\d+):(\d+)"
    match = re.match(pattern, timecode)
    if not match:
        raise ValueError(f"Invalid timecode format: {timecode}")

    hours, minutes, seconds, frames = map(int, match.groups())
    total_frames = (
        hours * 3600 * fps +
        minutes * 60 * fps +
        seconds * fps +
        frames
    )
    return total_frames

def frames_to_timecode(frames, fps):
    frames = round(frames)
    hours = frames // (3600 * fps)
    frames %= (3600 * fps)
    minutes = frames // (60 * fps)
    frames %= (60 * fps)
    seconds = frames // fps
    frames %= fps
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}:{int(frames):02}"

def calculate_total_duration():
    try:
        fps = float(fps_var.get())
        timecodes = timecode_text.get("1.0", "end").strip().split("\n")
        total_frames = 0
        for timecode in timecodes:
            if timecode.strip():
                total_frames += timecode_to_frames(timecode.strip(), fps)

        total_timecode = frames_to_timecode(total_frames, fps)
        result_text.delete("1.0", "end")
        result_text.insert("1.0", total_timecode)
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def calculate_subtracted_duration():
    try:
        fps = float(fps_var_sum.get())
        timecodes = timecode_text_sum.get("1.0", "end").strip().split("\n")

        if len(timecodes) != 2:
            raise ValueError("Please enter exactly two timecodes for subtraction.")

        total_frames = timecode_to_frames(timecodes[0].strip(), fps)
        total_frames -= timecode_to_frames(timecodes[1].strip(), fps)
        total_frames = abs(total_frames)

        total_timecode = frames_to_timecode(total_frames, fps)
        result_text_sum.delete("1.0", "end")
        result_text_sum.insert("1.0", total_timecode)
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def clear_fields():
    timecode_text.delete("1.0", "end")
    result_text.delete("1.0", "end")

def clear_fields_sum():
    timecode_text_sum.delete("1.0", "end")
    result_text_sum.delete("1.0", "end")

def copy_to_clipboard():
    total_duration = result_text.get("1.0", "end").strip()
    root.clipboard_clear()
    root.clipboard_append(total_duration)
    root.update()

def copy_to_clipboard_sum():
    total_duration = result_text_sum.get("1.0", "end").strip()
    root.clipboard_clear()
    root.clipboard_append(total_duration)
    root.update()

def main():
    global root, fps_var, timecode_text, result_text, fps_var_sum, timecode_text_sum, result_text_sum

    # Initialize ttkbootstrap root
    root = ttk.Window(themename="flatly")  # Changed theme to "flatly" for light gray background
    root.configure(bg="#f0f0f0")  # Set light gray background
    root.title("Timecode Calculator")
    root.geometry("600x400")
    root.minsize(600, 400)  # Set the minimum size of the window

    # Create notebook for tabs
    notebook = ttk.Notebook(root, bootstyle=PRIMARY)
    notebook.pack(fill=BOTH, expand=TRUE, padx=10, pady=10)

    # Duration Tab
    duration_tab = ttk.Frame(notebook)
    notebook.add(duration_tab, text="Duration TC")

    duration_tab.rowconfigure(1, weight=1)  # Allow text area to expand vertically
    duration_tab.rowconfigure(2, weight=0)  # Output field and buttons stay together
    duration_tab.columnconfigure(0, weight=1)  # Allow components to expand horizontally
    duration_tab.columnconfigure(1, weight=1)

    ttk.Label(duration_tab, text="Enter Timecodes (HH:MM:SS:FF):", bootstyle=INFO).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    fps_var = ttk.StringVar(value="23.976")
    fps_dropdown = ttk.Combobox(duration_tab, textvariable=fps_var, values=["23.976", "24", "25", "29.97", "30", "50", "59.94", "60"], bootstyle=SUCCESS)
    fps_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    timecode_frame = ttk.Frame(duration_tab)
    timecode_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    timecode_text = ttk.Text(timecode_frame, height=10, width=40, wrap="none")
    timecode_text.pack(side="left", fill="both", expand=True)

    timecode_scroll = ttk.Scrollbar(timecode_frame, orient="vertical", command=timecode_text.yview)
    timecode_scroll.pack(side="right", fill="y")
    timecode_text.configure(yscrollcommand=timecode_scroll.set)

    result_frame = ttk.Frame(duration_tab)
    result_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
    result_frame.columnconfigure(0, weight=1)
    result_frame.columnconfigure(1, weight=0)

    result_text = ttk.Text(result_frame, height=1, width=40, state="normal")
    result_text.grid(row=0, column=0, sticky="ew")
    ttk.Button(result_frame, text="Copy", command=copy_to_clipboard, bootstyle=SUCCESS).grid(row=0, column=1, padx=5, sticky="e")

    button_frame = ttk.Frame(duration_tab)
    button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)

    ttk.Button(button_frame, text="Calculate", command=calculate_total_duration, bootstyle=PRIMARY).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    ttk.Button(button_frame, text="Clear", command=clear_fields, bootstyle=WARNING).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # Subtract Tab
    subtract_tab = ttk.Frame(notebook)
    notebook.add(subtract_tab, text="Subtract TC")

    subtract_tab.rowconfigure(1, weight=1)  # Allow text area to expand vertically
    subtract_tab.rowconfigure(2, weight=0)  # Output field and buttons stay together
    subtract_tab.columnconfigure(0, weight=1)  # Allow components to expand horizontally
    subtract_tab.columnconfigure(1, weight=1)

    ttk.Label(subtract_tab, text="Enter Timecodes (HH:MM:SS:FF):", bootstyle=INFO).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    fps_var_sum = ttk.StringVar(value="23.976")
    fps_dropdown_sum = ttk.Combobox(subtract_tab, textvariable=fps_var_sum, values=["23.976", "24", "25", "29.97", "30", "50", "59.94", "60"], bootstyle=SUCCESS)
    fps_dropdown_sum.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    timecode_frame_sum = ttk.Frame(subtract_tab)
    timecode_frame_sum.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    timecode_text_sum = ttk.Text(timecode_frame_sum, height=10, width=40, wrap="none")
    timecode_text_sum.pack(side="left", fill="both", expand=True)

    timecode_scroll_sum = ttk.Scrollbar(timecode_frame_sum, orient="vertical", command=timecode_text_sum.yview)
    timecode_scroll_sum.pack(side="right", fill="y")
    timecode_text_sum.configure(yscrollcommand=timecode_scroll_sum.set)

    result_frame_sum = ttk.Frame(subtract_tab)
    result_frame_sum.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
    result_frame_sum.columnconfigure(0, weight=1)
    result_frame_sum.columnconfigure(1, weight=0)

    result_text_sum = ttk.Text(result_frame_sum, height=1, width=40, state="normal")
    result_text_sum.grid(row=0, column=0, sticky="ew")
    ttk.Button(result_frame_sum, text="Copy", command=copy_to_clipboard_sum, bootstyle=SUCCESS).grid(row=0, column=1, padx=5, sticky="e")

    button_frame_sum = ttk.Frame(subtract_tab)
    button_frame_sum.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
    button_frame_sum.columnconfigure(0, weight=1)
    button_frame_sum.columnconfigure(1, weight=1)

    ttk.Button(button_frame_sum, text="Subtract", command=calculate_subtracted_duration, bootstyle=PRIMARY).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    ttk.Button(button_frame_sum, text="Clear", command=clear_fields_sum, bootstyle=WARNING).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    root.mainloop()

if __name__ == "__main__":
    main()
