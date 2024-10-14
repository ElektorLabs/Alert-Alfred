# Version: V1.2.5
import gi
import os
import csv
import time
import requests
from datetime import datetime
import numpy as np
import cv2
import hailo
from gi.repository import Gst, GLib
from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from detection_pipeline import GStreamerDetectionApp

gi.require_version('Gst', '1.0')

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.new_variable = 42  # New variable example
        self.person_detected = False  # Track if a person is currently detected
        self.last_detected_time = None  # Track the last detection time
        self.detection_frame_count = 0  # Track the number of frames since the person was detected
        self.last_detection_time = 0  # Track the time of the last detection
        self.grace_period = 2  # Grace period in seconds before resetting detection status
        self.csv_log_path = "logs/detection_log.csv"  # Path to CSV log file in logs
        self.telegram_bot_token = "XXXXX"  # Telegram bot token
        self.telegram_chat_id = "XXXXX"  # Telegram chat ID
        self.setup_csv_log()  # Setup the CSV log file

    def new_function(self):  # New function example
        return "The meaning of life is: "

    def setup_csv_log(self):
        # Ensure logs directory exists
        if not os.path.exists("logs"):
            os.makedirs("logs")
        # Create CSV log if it doesn't exist
        if not os.path.exists(self.csv_log_path):
            with open(self.csv_log_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Event"])

    def log_event(self, event):
        # Append a new event to the CSV log
        with open(self.csv_log_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event])

    def send_telegram_alert(self, image_path, timestamp, detection_count):
        # Send the alert message and photo to the Telegram bot
        try:
            formatted_timestamp = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
            message = (f"🚨 Intruder Alert 🚨\n"
                       f"Date and Time: {formatted_timestamp}\n"
                       f"Detected Person(s): {detection_count}\n"
                       f"AI Security System Notification")
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message
            }
            requests.post(url, data=payload)

            # Send the image
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendPhoto"
            with open(image_path, "rb") as image_file:
                files = {
                    "photo": image_file
                }
                data = {
                    "chat_id": self.telegram_chat_id
                }
                requests.post(url, files=files, data=data)

            print(f"Alert sent to Telegram: {message}")
        except Exception as e:
            print(f"Exception while sending Telegram alert: {e}")

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------

# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    # Check if the buffer is valid
    if buffer is None:
        print("Warning: Received an empty buffer.")
        return Gst.PadProbeReturn.OK

    # Using the user_data to count the number of frames
    user_data.increment()
    string_to_print = f"Frame count: {user_data.get_count()}\n"

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    frame = None
    if format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)
        if frame is None or frame.size == 0:
            print("Warning: Empty frame received.")
            return Gst.PadProbeReturn.OK

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Parse the detections
    detection_count = 0
    person_detected = False
    for detection in detections:
        label = detection.get_label()
        confidence = detection.get_confidence()
        if label == "person":
            string_to_print += f"Detection: {label} {confidence:.2f}\n"
            detection_count += 1
            person_detected = True

    current_time = time.time()

    # Handle person detection logging and image saving
    if person_detected:
        user_data.last_detection_time = current_time  # Update the last detection time
        if not user_data.person_detected:
            # Log the person entry event
            user_data.log_event("Person entered the frame")
            user_data.person_detected = True
            user_data.last_detected_time = current_time
            user_data.detection_frame_count = 1
        else:
            user_data.detection_frame_count += 1

        # Save the frame as an image with a timestamp after 10 frames when a person is detected
        if user_data.detection_frame_count == 10:
            if frame is not None and frame.size > 0:
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = f"logs/person_detected_{timestamp}.png"
                    success = cv2.imwrite(image_path, frame)
                    if success:
                        print(f"Image saved at {image_path}")
                        # Send alert to Telegram
                        user_data.send_telegram_alert(image_path, timestamp, detection_count)
                    else:
                        print(f"Error: Failed to save image at {image_path}")
                except Exception as e:
                    print(f"Exception while saving image: {e}")

    else:
        # If no person is detected, check if the grace period has passed before resetting
        if user_data.person_detected and (current_time - user_data.last_detection_time > user_data.grace_period):
            # Log the person exit event
            user_data.log_event("Person exited the frame")
            user_data.person_detected = False
            user_data.detection_frame_count = 0

    print(string_to_print)
    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    try:
        app.run()
    except KeyboardInterrupt:
        print("Application stopped by user.")