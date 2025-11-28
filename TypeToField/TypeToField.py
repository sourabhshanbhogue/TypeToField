import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import pyautogui
import threading
import time
from ctypes import windll

user32 = windll.user32

# --- Add global stop flag and thread reference ---
typing_thread = None
stop_typing_flag = threading.Event()

# Function to type text using pyautogui
# Modified to check stop flag

def type_text(text):
    for char in text:
        if stop_typing_flag.is_set():
            break
        pyautogui.write(char)
        pyautogui.sleep(0.02)  # Small delay between keystrokes

# Wait for the user to focus a different window (the target)
def wait_for_focus_change(initial_handle, timeout=None):
    start = time.time()
    while True:
        try:
            current = user32.GetForegroundWindow()
        except Exception:
            current = None
        if current and current != initial_handle:
            return True
        if timeout is not None and (time.time() - start) > timeout:
            return False
        time.sleep(0.05)

# Thread entry: wait for focus or delay then optionally select target text and type
# Modified to check stop flag

def wait_and_type(text, wait_for_focus, delay_before, select_before):
    try:
        initial = user32.GetForegroundWindow()
    except Exception:
        initial = None

    if wait_for_focus:
        ok = wait_for_focus_change(initial, timeout=None)
        if not ok or stop_typing_flag.is_set():
            return
        time.sleep(0.12)
    else:
        if delay_before and delay_before > 0:
            for _ in range(int(delay_before * 20)):
                if stop_typing_flag.is_set():
                    return
                time.sleep(0.05)

    if select_before and not stop_typing_flag.is_set():
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.press('delete')
        time.sleep(0.05)

    if not stop_typing_flag.is_set():
        type_text(text)

    try:
        root.after(0, root.deiconify)
        root.after(0, root.lift)
    except Exception:
        pass

# Function to start typing in a separate thread
# Modified to set/clear stop flag and track thread

def start_typing():
    global typing_thread
    stop_typing_flag.clear()
    text = text_widget.get("1.0", "end-1c")
    if not text:
        return
    try:
        delay = float(delay_var.get())
    except Exception:
        delay = 0.0

    wait_for_focus = wait_focus_var.get()
    select_before = select_var.get()
    minimize = minimize_var.get()

    if minimize:
        try:
            root.iconify()
        except Exception:
            pass

    typing_thread = threading.Thread(target=wait_and_type, args=(text, wait_for_focus, delay, select_before), daemon=True)
    typing_thread.start()

# --- Add stop function ---
def stop_typing():
    stop_typing_flag.set()

# Create the main window
root = tk.Tk()
root.title("Type Into Text Field")
root.geometry("700x380")

label = tk.Label(root, text="Enter text to type (you can paste a paragraph): Click 'Type', then click inside the target field to start typing.")
label.pack(pady=(10, 0))

# Multi-line text widget with scrollbar to allow pasting long paragraphs
text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=12)
text_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# Define control variables
delay_var = tk.StringVar(value="0")
wait_focus_var = tk.BooleanVar(value=True)
minimize_var = tk.BooleanVar(value=True)
select_var = tk.BooleanVar(value=False)

controls_frame = tk.Frame(root)
controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

# Delay before typing (used when not waiting for focus)
delay_label = tk.Label(controls_frame, text="Delay before typing (seconds):")
delay_label.grid(row=0, column=0, sticky="w", pady=2)
delay_entry = tk.Entry(controls_frame, textvariable=delay_var, width=5)
delay_entry.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=2)

wait_focus_check = tk.Checkbutton(controls_frame, text="Wait for me to select the target field", variable=wait_focus_var)
wait_focus_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=2)

minimize_check = tk.Checkbutton(controls_frame, text="Minimize while typing", variable=minimize_var)
minimize_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)

select_check = tk.Checkbutton(controls_frame, text="Delete existing text (Ctrl+A+Dlt) before typing", variable=select_var)
select_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=2)

# Buttons
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=(0, 10))

type_button = tk.Button(buttons_frame, text="Type", command=start_typing)
type_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(buttons_frame, text="Clear", command=lambda: text_widget.delete("1.0", tk.END))
clear_button.pack(side=tk.LEFT, padx=5)

# --- Add Stop button ---
stop_button = tk.Button(buttons_frame, text="Stop", command=stop_typing)
stop_button.pack(side=tk.LEFT, padx=5)

root.mainloop()
