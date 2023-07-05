import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from PIL import ImageTk, Image

def show_alert(subject, message):
    messagebox.showinfo(subject, message)

def update_frame():
    global video_capture
    if video_capture is not None:
        # Read the video frame
        ret, frame = video_capture.read()
        if ret:
            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create an ImageTk object
            image_tk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

            # Update the label with the new image
            image_label.configure(image=image_tk)
            image_label.image = image_tk
            
            # Schedule the next frame update
            image_label.after(30, update_frame)
    else:
        # Display the placeholder image if no frame is available
        image_label.configure(image=placeholder_image)
        image_label.image = placeholder_image

def start_detection():
    global video_capture
    if video_capture is None:
        video_capture = cv2.VideoCapture(1)  # Use 0 for the default camera
        update_frame()
    else:
        show_alert("Information", "Detection is already running")
    

def stop_detection():
    global video_capture
    if video_capture is not None:
        video_capture.release()
        video_capture = None
        update_frame()
    else:
        show_alert("Information", "Detection is not running")

# Create the main window
window = tk.Tk()
window.title("Coconut Detection GUI")
video_capture = None

# Create the left frame
left_frame = ttk.Frame(window)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create the right frame
right_frame = ttk.Frame(window)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a text area in the left frame
text_area = tk.Text(left_frame, width=30, height=10)
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Increase the font size of the text area
text_font = font.Font(size=30)  # Adjust the font size as desired
text_area.configure(font=text_font)

# Create the start button
start_button = ttk.Button(left_frame, text="Start", command=start_detection)
start_button.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)

# Create a label to display the OpenCV frame
image_label = ttk.Label(right_frame)
image_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create the stop button
stop_button = ttk.Button(right_frame, text="Stop", command=stop_detection)
stop_button.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)

# Start with the placeholder image
placeholder_image = ImageTk.PhotoImage(Image.new('RGB', (400, 400)))
image_label.configure(image=placeholder_image)
image_label.image = placeholder_image

# Start the GUI event loop
window.mainloop()
