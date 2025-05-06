
# 📷 QR & Data Matrix Decoder Application

This project provides two intuitive interfaces to **detect and decode QR codes and Data Matrix codes**:

1. 🌐 A **modern Flask-based web application**  
2. 🖥️ A **desktop GUI application built with Tkinter**

---

## 🚀 Features

- 🔍 Detects **QR codes** and **Data Matrix codes** in images
- 🧠 Utilizes **YOLOv8** for robust and accurate detection
- 🖼️ Handles **multiple codes per image**
- 🧩 Displays **decoded data** with visual overlays
- 🌐 Web app supports **drag-and-drop** uploads
- 🖱️ Desktop app supports **file selection dialog**
- 📋 One-click copy of decoded content
- 🧪 Pre-packaged with sample images for testing

---

## 📦 Installation

### ✅ Prerequisites

- Python **3.8+**
- `pip` package manager

### 📥 Setup for Both Applications

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Lamouchi-Bayrem/Data-Matrix-scanner.git
   cd Data-Matrix-scanner


2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Download the YOLO model weights**:

   * Place `best.pt` in the root directory.

---

## 🌐 Web Application (Flask)

### ▶️ Running the Web App

```bash
python app.py
```

Access it at: [http://localhost:5000](http://localhost:5000)

### 🧭 Usage

* Open the web interface in your browser
* Drag and drop an image or click to select
* View decoded codes with bounding boxes
* Copy results to clipboard

### 📁 Web App Structure

```
web-app/
├── app.py                # Flask backend
├── requirements.txt      # Web dependencies
├── best.pt               # YOLOv8 model weights
├── uploads/              # Uploaded images
└── templates/
    └── index.html        # Web interface
```

---

## 🖥️ Desktop Application (Tkinter)

### ▶️ Running the Desktop App

```bash
python tkinter_app.py
```

### 🧭 Usage

* Launch the GUI
* Click **"Open Image"** to choose a file
* View decoded codes and visual highlights
* Save or copy results

### 📁 Desktop App Structure

```
desktop-app/
├── tkinter_app.py        # Desktop GUI
├── requirements.txt      # GUI dependencies
├── best.pt               # YOLOv8 model weights
└── samples/              # Example test images
```

---

## ⚙️ Performance Notes

* ⏱️ **Average processing time**: 500–1500 ms per image (depending on hardware)
* 📐 **Recommended image size**: 800–2000px per side
* 🖼️ **Supported formats**: PNG, JPG, JPEG, BMP

---

## 🧰 Troubleshooting

### ❌ No codes detected?

* Ensure the image has good lighting
* Try a higher resolution image
* Lower the confidence threshold if needed

### ❌ Installation errors?

* Verify Python version (3.8+)
* If using GPU, ensure CUDA is configured correctly

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.


