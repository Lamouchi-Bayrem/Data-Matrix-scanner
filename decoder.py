import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextEdit, QComboBox, QScrollArea, 
                            QFileDialog, QMessageBox, QStatusBar, QFrame)
from PyQt5.QtGui import QImage, QPixmap, QTextCursor, QFont, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QThread
from PyQt5.QtMultimedia import QCameraInfo, QCamera
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import webbrowser
from datetime import datetime
import pyperclip

class CameraThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.running = True
        
    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frame_ready.emit(frame)
        cap.release()
        
    def stop(self):
        self.running = False
        self.wait()

class CodeScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔍 Advanced QR & Data Matrix Scanner")
        self.setGeometry(100, 100, 1000, 850)
        self.setMinimumSize(900, 750)
        
        # Initialize status bar first
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Initializing...")
        
        # Dark theme colors
        self.bg_color = "#1c1c1c"
        self.primary_color = "#2e2e2e"
        self.secondary_color = "#4b4b4b"
        self.success_color = "#8f8f8f"
        self.danger_color = "#a3a3a3"
        self.text_color = "#eaeaea"
        self.highlight_color = "#ffffff"
        
        # Initialize variables
        self.camera_thread = None
        self.scan_count = 0
        self.last_scan_time = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header section
        header = QHBoxLayout()
        title = QLabel("Advanced QR & Data Matrix Scanner")
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {self.highlight_color};")
        header.addWidget(title)
        
        header.addStretch()
        
        self.stats_btn = QPushButton("📊 Stats")
        self.stats_btn.setStyleSheet(self.get_button_style())
        self.stats_btn.clicked.connect(self.show_stats)
        header.addWidget(self.stats_btn)
        
        self.help_btn = QPushButton("ℹ️ Help")
        self.help_btn.setStyleSheet(self.get_button_style())
        self.help_btn.clicked.connect(self.show_help)
        header.addWidget(self.help_btn)
        
        main_layout.addLayout(header)
        
        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(f"background-color: {self.primary_color}; border: 1px solid {self.secondary_color};")
        self.image_label.setMinimumHeight(400)
        main_layout.addWidget(self.image_label, 1)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("📁 Load Image")
        self.load_btn.setStyleSheet(self.get_button_style())
        self.load_btn.clicked.connect(self.load_image)
        btn_layout.addWidget(self.load_btn)
        
        self.clear_btn = QPushButton("🧹 Clear")
        self.clear_btn.setStyleSheet(self.get_button_style())
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)
        
        btn_layout.addStretch()
        
        self.copy_btn = QPushButton("⎘ Copy")
        self.copy_btn.setStyleSheet(self.get_button_style())
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.copy_btn)
        
        self.export_btn = QPushButton("💾 Export Results")
        self.export_btn.setStyleSheet(self.get_button_style())
        self.export_btn.clicked.connect(self.export_results)
        btn_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(btn_layout)
        
        # Live detection section
        live_frame = QFrame()
        live_frame.setFrameShape(QFrame.StyledPanel)
        live_frame.setStyleSheet(f"QFrame {{ border: 1px solid {self.secondary_color}; border-radius: 4px; }}")
        live_layout = QVBoxLayout(live_frame)
        
        live_title = QLabel("🎥 Live Detection")
        live_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {self.highlight_color};")
        live_layout.addWidget(live_title)
        
        # Camera selection
        cam_layout = QHBoxLayout()
        cam_layout.addWidget(QLabel("Camera:"))
        
        self.camera_combo = QComboBox()
        self.camera_combo.setStyleSheet(f"""
            QComboBox {{
                background: {self.primary_color};
                color: {self.text_color};
                border: 1px solid {self.secondary_color};
                padding: 5px;
                min-width: 80px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        cam_layout.addWidget(self.camera_combo)
        
        self.refresh_cam_btn = QPushButton("🔄 Refresh")
        self.refresh_cam_btn.setStyleSheet(self.get_button_style())
        self.refresh_cam_btn.clicked.connect(self.detect_cameras)
        cam_layout.addWidget(self.refresh_cam_btn)
        
        live_layout.addLayout(cam_layout)
        
        # Camera controls
        cam_btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Scanning")
        self.start_btn.setStyleSheet(self.get_button_style())
        self.start_btn.clicked.connect(self.start_camera)
        cam_btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setStyleSheet(self.get_button_style())
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        cam_btn_layout.addWidget(self.stop_btn)
        
        cam_btn_layout.addStretch()
        
        self.snapshot_btn = QPushButton("📸 Take Snapshot")
        self.snapshot_btn.setStyleSheet(self.get_button_style())
        self.snapshot_btn.clicked.connect(self.take_snapshot)
        self.snapshot_btn.setEnabled(False)
        cam_btn_layout.addWidget(self.snapshot_btn)
        
        live_layout.addLayout(cam_btn_layout)
        main_layout.addWidget(live_frame)
        
        # Results display
        result_frame = QFrame()
        result_frame.setFrameShape(QFrame.StyledPanel)
        result_frame.setStyleSheet(f"QFrame {{ border: 1px solid {self.secondary_color}; border-radius: 4px; }}")
        result_layout = QVBoxLayout(result_frame)
        
        result_title = QLabel("🧾 Decoded Data")
        result_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {self.highlight_color};")
        result_layout.addWidget(result_title)
        
        self.result_text = QTextEdit()
        self.result_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.primary_color};
                color: #00ff99;
                border: 1px solid {self.secondary_color};
                font-family: Consolas;
                font-size: 11px;
            }}
        """)
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        
        main_layout.addWidget(result_frame, 1)
        
        # Configure status bar style
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {self.primary_color};
                color: {self.text_color};
                border-top: 1px solid {self.secondary_color};
                font-size: 9px;
            }}
        """)
        
        # Set window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.bg_color};
                color: {self.text_color};
            }}
            QLabel {{
                color: {self.text_color};
            }}
        """)
        
        # Now detect cameras
        self.detect_cameras()
    
    def get_button_style(self):
        return f"""
            QPushButton {{
                background-color: {self.primary_color};
                color: {self.text_color};
                border: 1px solid {self.secondary_color};
                border-radius: 4px;
                padding: 6px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.secondary_color};
            }}
            QPushButton:pressed {{
                background-color: {self.highlight_color};
                color: {self.bg_color};
            }}
        """
    
    def update_status(self, message):
        """Update the status bar with a message"""
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.status_bar.showMessage(f"[{timestamp}] {message}")
        
    def show_help(self):
        """Show help information"""
        help_text = """QR & Data Matrix Scanner Help:

1. Load Image: Open an image file containing QR/Data Matrix codes
2. Live Detection: Use your camera to scan codes in real-time
3. Export Results: Save decoded data to a text file
4. Copy: Copy results to clipboard

Supported code types: QR Code, Data Matrix, UPC-A, UPC-E, EAN-8, EAN-13, etc.
"""
        QMessageBox.information(self, "Help", help_text)
        
    def show_stats(self):
        """Show scanning statistics"""
        stats = f"Scan Statistics:\n\nTotal scans: {self.scan_count}"
        if self.last_scan_time:
            stats += f"\nLast scan: {self.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}"
        QMessageBox.information(self, "Statistics", stats)
        
    def export_results(self):
        """Export results to a text file"""
        content = self.result_text.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "Export", "No results to export!")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "",
            "Text files (*.txt);;All files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(content)
                self.update_status(f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
                
    def copy_to_clipboard(self):
        """Copy results to clipboard"""
        content = self.result_text.toPlainText()
        if content.strip():
            pyperclip.copy(content)
            self.update_status("Results copied to clipboard")
        else:
            QMessageBox.warning(self, "Copy", "No results to copy!")

    def detect_cameras(self):
        """Detect available cameras"""
        self.update_status("Detecting cameras...")
        self.camera_combo.clear()
        
        cameras = QCameraInfo.availableCameras()
        for i, camera in enumerate(cameras):
            self.camera_combo.addItem(f"Camera {i} - {camera.description()}", i)
            
        if cameras:
            self.update_status(f"Found {len(cameras)} camera(s). Ready to scan.")
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
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image files (*.png *.jpg *.jpeg *.bmp *.tiff);;All files (*)"
        )
        if not file_path:
            return

        try:
            image = cv2.imread(file_path)
            if image is None:
                QMessageBox.critical(self, "Error", "Could not read the image file.")
                return

            self.update_status(f"Processing {file_path}...")
            image, decoded_info = self.decode_image(image)
            self.show_image(image)
            self.display_result(decoded_info)
            self.scan_count += 1
            self.last_scan_time = datetime.now()
            self.update_status(f"Found {len(decoded_info)} code(s) in the image")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process image: {str(e)}")
            self.update_status("Image processing failed")

    def show_image(self, cv_img):
        """Display the image in the GUI"""
        # Calculate dimensions to maintain aspect ratio
        height, width = cv_img.shape[:2]
        bytes_per_line = 3 * width
        q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        
        # Scale the image to fit while maintaining aspect ratio
        scaled_pixmap = QPixmap.fromImage(q_img).scaled(
            self.image_label.width(), 
            self.image_label.height(), 
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)

    def display_result(self, info_list):
        """Display the decoded results"""
        self.result_text.clear()
        if info_list:
            for line in info_list:
                self.result_text.append(line)
                
                # Highlight URLs
                if line.lower().startswith(("http://", "https://")):
                    cursor = self.result_text.textCursor()
                    cursor.movePosition(QTextCursor.StartOfLine)
                    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                    
                    fmt = QTextCharFormat()
                    fmt.setForeground(QColor("#1e90ff"))
                    fmt.setAnchor(True)
                    fmt.setAnchorHref(line.split(": ")[1])
                    cursor.mergeCharFormat(fmt)
                    self.result_text.setTextCursor(cursor)
                    
            # Scroll to top
            self.result_text.moveCursor(QTextCursor.Start)
        else:
            self.result_text.setText("❌ No QR/Data Matrix code detected.")

    def clear_all(self):
        """Clear the current image and results"""
        self.image_label.clear()
        self.result_text.clear()
        self.update_status("Ready")

    def start_camera(self):
        """Start the camera for live scanning"""
        if self.camera_thread and self.camera_thread.isRunning():
            return
            
        if self.camera_combo.count() == 0:
            QMessageBox.critical(self, "Error", "No camera selected!")
            return
            
        cam_index = self.camera_combo.currentData()
        self.camera_thread = CameraThread(cam_index)
        self.camera_thread.frame_ready.connect(self.process_frame)
        self.camera_thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.snapshot_btn.setEnabled(True)
        self.update_status(f"Live scanning started (Camera {cam_index})")

    def stop_camera(self):
        """Stop the live camera feed"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None
            
        self.image_label.clear()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.snapshot_btn.setEnabled(False)
        self.update_status("Live scanning stopped")

    def take_snapshot(self):
        """Take a snapshot from the live camera"""
        if not self.camera_thread or not self.camera_thread.isRunning():
            QMessageBox.warning(self, "Snapshot", "Camera is not active!")
            return
            
        # Save the current frame
        if hasattr(self, 'current_frame'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.png"
            cv2.imwrite(filename, self.current_frame)
            self.update_status(f"Snapshot saved as {filename}")
            
            # Also process the snapshot
            frame, decoded_info = self.decode_image(self.current_frame.copy())
            self.show_image(frame)
            self.display_result(decoded_info)
            self.scan_count += 1
            self.last_scan_time = datetime.now()

    def process_frame(self, frame):
        """Process each frame from the camera"""
        self.current_frame = frame.copy()
        decoded_frame, info = self.decode_image(frame)
        self.show_image(decoded_frame)
        
        if info:  # Only update results if something was detected
            self.display_result(info)
            self.scan_count += 1
            self.last_scan_time = datetime.now()

    def closeEvent(self, event):
        """Clean up when closing the application"""
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeScannerApp()
    window.show()
    sys.exit(app.exec_())
