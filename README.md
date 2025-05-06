# QR & Data Matrix Decoder Application

This application provides two interfaces for decoding QR codes and Data Matrix codes:
1. A **Flask-based web application** with modern UI/UX
2. A **Tkinter-based desktop GUI** application

## Features

- Detects and decodes both QR codes and Data Matrix codes
- Supports multiple codes in a single image
- Displays decoded data with visualization
- Web version includes drag-and-drop functionality
- Desktop version offers simple file selection
- Robust detection using YOLOv8 and specialized libraries

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### For Both Versions

1. Clone the repository:
   ```bash
   git clone https://https://github.com/Lamouchi-Bayrem/Data-Matrix-scanner.git
   cd qr-datamatrixdecoder
   Install required dependencies:

bash
pip install -r requirements.txt
Download the YOLO model file (best.pt) and place it in the project root directory

Web Application (Flask)
Running the Web App
bash
python app.py
The application will be available at: http://localhost:5000

Usage
Open the web interface in your browser

Drag and drop an image or click to select

View decoded results with visual highlights

Copy decoded data to clipboard

Web App Structure
web-app/
├── app.py                # Flask application
├── requirements.txt      # Python dependencies
├── best.pt              # YOLO model weights
├── uploads/             # Folder for uploaded images
└── templates/
    └── index.html       # Frontend interface
Desktop Application (Tkinter)
Running the Desktop App
bash
python tkinter_app.py
Usage
Launch the application

Click "Open Image" to select an image file

View decoded results in the text area

See visual feedback on the image

Save results or copy to clipboard

Desktop App Structure
desktop-app/
├── tkinter_app.py       # Tkinter application
├── requirements.txt     # Python dependencies
├── best.pt             # YOLO model weights
└── samples/            # Sample images for testing
Performance Notes
Average processing time: 500-1500ms per image (varies by hardware)

Recommended image size: 800-2000px per side

Supported formats: PNG, JPG, JPEG, BMP

Troubleshooting
Common Issues:

No codes detected:

Ensure proper lighting in the image

Try higher resolution images

Check minimum confidence threshold

Installation errors:

Verify Python version (3.8+ required)

Ensure CUDA is properly configured if using GPU

License
MIT License - See LICENSE for details
