# alert-alfred: AI Security System with Person Detection and Telegram Alerts

## Overview
alert-alfred is an AI-powered security system that uses computer vision to detect people in a video stream. It logs the detection events, saves images of the detected persons, and sends notifications via Telegram. alert-alfred is designed to run on an ESP-based detection pipeline using GStreamer, Hailo AI, and OpenCV for processing. This project is based on the [hailo-rpi5-examples GitHub repository](https://github.com/hailo-ai/hailo-rpi5-examples), which provides a starting point for utilizing Hailo's AI capabilities on embedded systems.

### Key Features
- **👤 Person Detection**: Identifies persons in the video stream.
- **📝 Event Logging**: Logs entry and exit events into a CSV file.
- **📸 Image Capture**: Captures an image when a person is detected.
- **📲 Telegram Alerts**: Sends a real-time notification, along with an image, to a specified Telegram chat.
- **⏳ Grace Period**: To avoid repeated notifications, the system implements a 2-second grace period before resetting detection status.

## Requirements
### Software Dependencies
- **Python 3.x**
- **GStreamer 1.0**
- **GObject Introspection (`gi`)**
- **OpenCV (`cv2`)**
- **Hailo SDK**
- **Telegram Bot API**
- Additional Python Libraries: `numpy`, `requests`

### Hardware Requirements
- **ESP32 or Raspberry Pi** for running the detection pipeline.
- **📹 Camera** compatible with GStreamer for video feed.
- **Hailo AI Module** for person detection.

## Setup Instructions

### Step 1: Clone the Hailo rpi5 Examples Repository
- Clone the [hailo-rpi5-examples GitHub repository](https://github.com/hailo-ai/hailo-rpi5-examples):
  ```bash
  git clone https://github.com/hailo-ai/hailo-rpi5-examples.git
  ```
- Follow the documentation in [`hailo-rpi5-examples/doc/basic-pipelines.md`](https://github.com/hailo-ai/hailo-rpi5-examples/blob/main/doc/basic-pipelines.md) to set up the environment.

### Step 2: Install Dependencies
1. **Install Python Packages**:
   ```bash
   pip install opencv-python numpy requests
   ```

2. **Install GStreamer**:
   Follow the instructions for installing GStreamer on your platform. For Linux:
   ```bash
   sudo apt-get install libgstreamer1.0-dev gstreamer1.0-tools gstreamer1.0-plugins-good
   ```

3. **Hailo SDK Installation**:
   Follow the instructions to install the Hailo SDK from their official website.

### Step 3: Set Up the Telegram Bot
1. **🤖 Create a Telegram Bot**:
   - Open Telegram and search for **BotFather**.
   - Create a new bot to receive your bot token (`YOUR_TELEGRAM_BOT_TOKEN`).

2. **Get the Chat ID**:
   - Use the bot to get the chat ID where you want to receive alerts.

### Step 4: Configure the Script
- Place the `alert-alfred.py` file into the `basic_pipelines/` folder of the `hailo-rpi5-examples` repository.
- Open the script and replace `YOUR_TELEGRAM_BOT_TOKEN` and `YOUR_CHAT_ID` with your bot token and chat ID.

### Step 5: Run the Script
- **Navigate to the `hailo-rpi5-examples` folder**, these steps are also mentioned in the `hailo-rpi5-examples/doc/basic-pipelines.md`:
  ```bash
  # Navigate to the hailo-rpi5-examples folder
  cd hailo-rpi5-examples
  # Activate the virtual environment
  source setup_env.sh
  # Requirements installation
  pip install -r requirements.txt
  sudo apt install -y rapidjson-dev
  # Download Resources
  python download_resources.py
  ```
- **Run the Python Script**:
Before running the script, ensure that the camera is camrea is    
connected and working properly, **to monitor a CCTV feed, and to stream the CCTV feed on a virtual display on the Raspberry Pi, please follow this [guide](docs/cctv-to-virtualcam-guide.md)**.
  ```bash
  python basic_pipelines/alert-alfred.py --input /dev/video10
  
  # OR if using a webcam:
  python basic_pipelines/alert-alfred.py --input /dev/video1 
  ```
- The script will start streaming from the camera, detect people, log events, save images, and send alerts.

## How It Works
1. **🖼️ Frame Processing**: The video feed from the camera is processed using GStreamer, which passes each frame to Hailo's AI model for person detection.
2. **🔍 Detection Logic**: If a person is detected for 10 consecutive frames, a snapshot is saved locally, and an alert message is sent to a specified Telegram chat.
3. **🗃️ Logging**: Events such as person entry and exit are logged in a CSV file, and a grace period of 2 seconds is used to prevent redundant notifications.

## Code Explanation
The script is organized as follows:
- **Class Definition (`user_app_callback_class`)**: This class manages the person detection status, logs events, and sends Telegram alerts.
- **Callback Function (`app_callback`)**: This function processes each frame, manages detection, saves snapshots, and triggers alerts.
- **Main Execution**: The script initializes the GStreamer app and starts processing the video feed.

## Future Improvements
- **🚗 Multi-Object Detection**: Extend the system to detect other types of objects (e.g., vehicles).
- **🛠️ Improved Notification Logic**: Add additional information or triggers for other events (e.g., no motion detected for extended periods).
- **🌐 Web Interface**: Develop a web interface to view logs, images, and configure settings remotely.

## Troubleshooting
- **⚠️ Buffer Allocation Error**: If you encounter a buffer allocation error, try increasing the buffer size in the GStreamer pipeline.
- **🚫 Telegram Alerts Not Sent**: Ensure the bot token and chat ID are correctly set and that the bot has permission to send messages to the chat.

## License
This project is licensed under the CC0 1.0 Universal.
