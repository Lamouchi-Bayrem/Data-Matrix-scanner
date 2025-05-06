import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import threading
import webbrowser
from datetime import datetime

class CodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Advanced QR & Data Matrix Scanner")
        self.root.geometry("1000x850")
        # Enhanced UI/UX Theme Colors
# Sleek Monochrome Theme
        self.root.configure(bg="#1c1c1c")  # Deep black-gray background
        self.root.minsize(900, 750)

        self.bg_color = "#1c1c1c"          # Background (almost black)
        self.primary_color = "#2e2e2e"     # Dark gray (panels/buttons)
        self.secondary_color = "#4b4b4b"   # Medium gray (hover, borders)
        self.success_color = "#8f8f8f"     # Soft gray (success)
        self.danger_color = "#a3a3a3"      # Lighter gray (warnings/errors)
        self.text_color = "#eaeaea"        # Almost white (text)
        self.highlight_color = "#ffffff"   # White (hover effects, highlights)


        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6)
        self.style.configure('TCombobox', padding=5)
        self.style.map('TButton',
                      background=[('active', self.primary_color), ('!disabled', self.primary_color)],
                      foreground=[('!disabled', 'white')])
        self.style.configure('Title.TLabel', font=('Segoe UI', 22, 'bold'), foreground=self.highlight_color)
        self.style.configure('Section.TLabelframe', font=('Segoe UI', 12, 'bold'), 
                           foreground=self.highlight_color, background=self.bg_color)
        self.style.configure('Result.TText', font=('Consolas', 11), background="#1e1e1e", 
                           foreground="#00ff99", insertbackground="white")
        self.style.configure('Status.TLabel', font=('Segoe UI', 9), background="#1e1e1e", 
                           foreground="#aaaaaa", relief="sunken", anchor="w")

        # Initialize variables
        self.video_capture = None
        self.live_thread = None
        self.running = False
        self.last_scan_time = None
        self.scan_count = 0
        self.status_var = tk.StringVar()  # Initialize status_var here
        self.status_var.set("Ready")  # Set initial status

        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Header Section ---
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Title
        title = ttk.Label(header_frame, text="Advanced QR & Data Matrix Scanner", 
                         style="Title.TLabel")
        title.pack(side="left")
        
        # Version/Help
        help_btn = ttk.Button(header_frame, text="ℹ️ Help", command=self.show_help, 
                            style='TButton', width=8)
        help_btn.pack(side="right", padx=5)
        
        stats_btn = ttk.Button(header_frame, text="📊 Stats", command=self.show_stats, 
                             style='TButton', width=8)
        stats_btn.pack(side="right", padx=5)

        # --- Image Display Section ---
        img_container = ttk.Frame(self.main_frame)
        img_container.pack(fill="both", expand=True)
        
        self.image_frame = ttk.Label(img_container, background="#1e1e1e")
        self.image_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # --- Control Buttons ---
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill="x", pady=5)
        
        self.load_btn = ttk.Button(btn_frame, text="📁 Load Image", command=self.load_image, 
                                  style='TButton')
        self.load_btn.pack(side="left", padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="🧹 Clear", command=self.clear_all, 
                                   style='TButton')
        self.clear_btn.pack(side="left", padx=5)
        
        self.export_btn = ttk.Button(btn_frame, text="💾 Export Results", command=self.export_results, 
                                   style='TButton')
        self.export_btn.pack(side="right", padx=5)
        
        self.copy_btn = ttk.Button(btn_frame, text="⎘ Copy", command=self.copy_to_clipboard, 
                                 style='TButton')
        self.copy_btn.pack(side="right", padx=5)

        # --- Live Detection Section ---
        live_frame = ttk.LabelFrame(self.main_frame, text="🎥 Live Detection", 
                                   style="Section.TLabelframe")
        live_frame.pack(fill="x", pady=10)
        
        # Camera selection
        cam_select_frame = ttk.Frame(live_frame)
        cam_select_frame.pack(fill="x", pady=5)
        
        ttk.Label(cam_select_frame, text="Camera:").pack(side="left", padx=(0, 5))
        self.camera_var = tk.StringVar()
        self.camera_list = ttk.Combobox(cam_select_frame, textvariable=self.camera_var, width=5)
        self.camera_list.pack(side="left", padx=5)
        self.detect_cameras()
        
        self.refresh_cam_btn = ttk.Button(cam_select_frame, text="🔄 Refresh", 
                                        command=self.detect_cameras, style='TButton')
        self.refresh_cam_btn.pack(side="left", padx=5)
        
        # Camera controls
        cam_ctrl_frame = ttk.Frame(live_frame)
        cam_ctrl_frame.pack(fill="x", pady=5)
        
        self.start_btn = ttk.Button(cam_ctrl_frame, text="▶️ Start Scanning", command=self.start_camera, 
                                  style='TButton')
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(cam_ctrl_frame, text="⏹ Stop", command=self.stop_camera, 
                                 style='TButton')
        self.stop_btn.pack(side="left", padx=5)
        
        self.snapshot_btn = ttk.Button(cam_ctrl_frame, text="📸 Take Snapshot", command=self.take_snapshot, 
                                     style='TButton')
        self.snapshot_btn.pack(side="right", padx=5)

        # --- Results Display ---
        result_frame = ttk.LabelFrame(self.main_frame, text="🧾 Decoded Data", 
                                    style="Section.TLabelframe")
        result_frame.pack(fill="both", expand=True)
        
        # Result text with scrollbar
        result_container = ttk.Frame(result_frame)
        result_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(result_container)
        scrollbar.pack(side="right", fill="y")
        
        self.result_text = tk.Text(result_container, height=8, wrap="word", 
                                  yscrollcommand=scrollbar.set)
        self.result_text.configure(font=("Consolas", 11), bg="#1e1e1e", fg="#00ff99", 
                                 insertbackground="white")
        self.result_text.pack(fill="both", expand=True)
        
        scrollbar.config(command=self.result_text.yview)
        
        # --- Status Bar ---
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var,
                                  style='Status.TLabel', padding=(5, 2))
        self.status_bar.pack(fill="x", pady=(5, 0))

    def update_status(self, message):
        """Update the status bar with a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"[{timestamp}] {message}")
        
    def show_help(self):
        """Show help information"""
        help_text = """QR & Data Matrix Scanner Help:

1. Load Image: Open an image file containing QR/Data Matrix codes
2. Live Detection: Use your camera to scan codes in real-time
3. Export Results: Save decoded data to a text file
4. Copy: Copy results to clipboard

Supported code types: QR Code, Data Matrix, UPC-A, UPC-E, EAN-8, EAN-13, etc.
"""
        messagebox.showinfo("Help", help_text)
        
    def show_stats(self):
        """Show scanning statistics"""
        stats = f"Scan Statistics:\n\nTotal scans: {self.scan_count}"
        if self.last_scan_time:
            stats += f"\nLast scan: {self.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}"
        messagebox.showinfo("Statistics", stats)
        
    def export_results(self):
        """Export results to a text file"""
        content = self.result_text.get("1.0", tk.END)
        if not content.strip():
            messagebox.showwarning("Export", "No results to export!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(content)
                self.update_status(f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
                
    def copy_to_clipboard(self):
        """Copy results to clipboard"""
        content = self.result_text.get("1.0", tk.END)
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.update_status("Results copied to clipboard")
        else:
            messagebox.showwarning("Copy", "No results to copy!")

    def detect_cameras(self):
        """Detect available cameras"""
        self.update_status("Detecting cameras...")
        indexes = []
        for i in range(5):  # Try first 5 indexes
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                indexes.append(str(i))
            cap.release()
            
        self.camera_list['values'] = indexes
        if indexes:
            self.camera_var.set(indexes[0])
            self.update_status(f"Found {len(indexes)} camera(s). Ready to scan.")
        else:
            self.update_status("No cameras detected!")
            
    def decode_image(self, image):
        """Decode QR/Data Matrix codes in the image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(gray)

        info = []
        for obj in decoded_objects:
            # Draw bounding box
            points = obj.polygon
            if len(points) == 4:
                pts = np.array(points, np.int32).reshape((-1, 1, 2))
                cv2.polylines(image, [pts], True, (0, 255, 0), 2)

            data = obj.data.decode("utf-8")
            label = f"{obj.type}: {data}"
            info.append(label)

            # Draw code type label
            cv2.putText(image, obj.type, (obj.rect.left, obj.rect.top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        return image, info

    def load_image(self):
        """Load an image file for scanning"""
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
                      ("All files", "*.*")]
        )
        if not path:
            return

        try:
            image = cv2.imread(path)
            if image is None:
                messagebox.showerror("Error", "Could not read the image file.")
                return

            self.update_status(f"Processing {path}...")
            image, decoded_info = self.decode_image(image)
            self.show_image(image)
            self.display_result(decoded_info)
            self.scan_count += 1
            self.last_scan_time = datetime.now()
            self.update_status(f"Found {len(decoded_info)} code(s) in the image")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
            self.update_status("Image processing failed")

    def show_image(self, cv_img):
        """Display the image in the GUI"""
        # Calculate dimensions to maintain aspect ratio
        max_height = 500
        max_width = 800
        
        height, width = cv_img.shape[:2]
        ratio = min(max_height/height, max_width/width)
        new_height = int(height * ratio)
        new_width = int(width * ratio)
        
        resized = cv2.resize(cv_img, (new_width, new_height))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        
        self.image_frame.configure(image=img)
        self.image_frame.image = img

    def display_result(self, info_list):
        """Display the decoded results"""
        self.result_text.delete("1.0", tk.END)
        if info_list:
            self.result_text.insert(tk.END, "\n".join(info_list))
            # Highlight URLs
            for line in info_list:
                if line.lower().startswith(("http://", "https://")):
                    self.result_text.tag_configure("url", foreground="#1e90ff", underline=1)
                    start = f"1.0 + {info_list.index(line)} lines linestart"
                    end = f"{start} lineend"
                    self.result_text.tag_add("url", start, end)
                    self.result_text.tag_bind("url", "<Button-1>", 
                                            lambda e, url=line.split(": ")[1]: webbrowser.open(url))
        else:
            self.result_text.insert(tk.END, "❌ No QR/Data Matrix code detected.")

    def clear_all(self):
        """Clear the current image and results"""
        self.image_frame.configure(image=None)
        self.image_frame.image = None
        self.result_text.delete("1.0", tk.END)
        self.update_status("Ready")

    def start_camera(self):
        """Start the camera for live scanning"""
        if self.running:
            return
            
        if not self.camera_var.get():
            messagebox.showerror("Error", "No camera selected!")
            return
            
        cam_index = int(self.camera_var.get())
        self.video_capture = cv2.VideoCapture(cam_index)
        
        if not self.video_capture.isOpened():
            messagebox.showerror("Error", "Could not open camera!")
            return
            
        self.running = True
        self.live_thread = threading.Thread(target=self.update_frame, daemon=True)
        self.live_thread.start()
        self.update_status(f"Live scanning started (Camera {cam_index})")

    def stop_camera(self):
        """Stop the live camera feed"""
        self.running = False
        if self.video_capture:
            self.video_capture.release()
        self.image_frame.configure(image=None)
        self.image_frame.image = None
        self.update_status("Live scanning stopped")

    def take_snapshot(self):
        """Take a snapshot from the live camera"""
        if not self.running or not self.video_capture:
            messagebox.showwarning("Snapshot", "Camera is not active!")
            return
            
        ret, frame = self.video_capture.read()
        if ret:
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.png"
            cv2.imwrite(filename, frame)
            self.update_status(f"Snapshot saved as {filename}")
            
            # Also process the snapshot
            frame, decoded_info = self.decode_image(frame)
            self.show_image(frame)
            self.display_result(decoded_info)
            self.scan_count += 1
            self.last_scan_time = datetime.now()

    def update_frame(self):
        """Update the camera frame continuously"""
        while self.running and self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            if not ret:
                break

            decoded_frame, info = self.decode_image(frame)
            
            # Update GUI in the main thread
            self.root.after(0, lambda: self.show_image(decoded_frame))
            if info:  # Only update results if something was detected
                self.root.after(0, lambda: self.display_result(info))
                self.root.after(0, lambda: setattr(self, 'scan_count', self.scan_count + 1))
                self.root.after(0, lambda: setattr(self, 'last_scan_time', datetime.now()))

            # Control frame rate
            cv2.waitKey(30)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = CodeScannerApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"The application crashed:\n{str(e)}")