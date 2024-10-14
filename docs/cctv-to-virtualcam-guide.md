For getting the AlertAlfred to work with a CCTV camera, we need to stream the CCTV footage to a virtual camera using the `v4l2loopback` kernel module. This will allow us to use the virtual camera as a source for the AlertAlfred.

Here's how to set up the virtual cameras on a Raspberry Pi:

### Step 1: Install Required Packages
The first step is to install the required packages:
```bash
sudo apt-get update
sudo apt-get install v4l2loopback-dkms
sudo apt-get install ffmpeg
```

### Step 2: Create the Virtual Cameras
To make the virtual cameras (`/dev/video10`, `/dev/video11`, `/dev/video12`) permanent across reboots, you'll need to ensure that the `v4l2loopback` kernel module is loaded automatically with the desired parameters every time your Raspberry Pi boots up. Here’s how you can do that:

The first step is to load the `v4l2loopback` module at boot by adding it to the system modules list.

1. **Create a Module Load Configuration File**:
   
   Create a file in `/etc/modules-load.d/` to load the `v4l2loopback` module:

   ```bash
   echo "v4l2loopback" | sudo tee /etc/modules-load.d/v4l2loopback.conf
   ```

   This ensures that the module is loaded at boot.

### Step 3: Create a Modprobe Configuration File for Parameters
Next, we need to define the parameters that should be used when the module is loaded. This will create the virtual video devices with the correct numbers and labels.

1. **Create a Module Parameters Configuration File**:

   Create a file in `/etc/modprobe.d/` to set the module options:

   ```bash
   sudo nano /etc/modprobe.d/v4l2loopback.conf
   ```

2. **Add the Following Configuration to the File**:

   ```conf
   options v4l2loopback video_nr=10,11,12 card_label="Virtual Camera 1","Virtual Camera 2","Virtual Camera 3" exclusive_caps=1
   ```

   - **`video_nr=10,11,12`**: Specifies the virtual devices numbers (`/dev/video10`, `/dev/video11`, `/dev/video12`).
   - **`card_label="Virtual Camera 1","Virtual Camera 2","Virtual Camera 3"`**: Assigns labels to each virtual camera.
   - **`exclusive_caps=1`**: Ensures exclusive access for each camera, useful for compatibility.

3. **Save and Exit**: Press `Ctrl + X`, then `Y`, and press `Enter` to save and exit the editor.

### Step 4: Update the Initramfs (Optional)
On some systems, it may be necessary to update the initramfs to include the new module settings, so that it is loaded correctly at boot.

Run the following command to update the initramfs:

```bash
sudo update-initramfs -u
```

### Step 4: Reboot and Verify
Now, reboot your Raspberry Pi to see if the virtual cameras are correctly created on startup:

```bash
sudo reboot
```

After rebooting, you can verify the virtual cameras by running:

```bash
v4l2-ctl --list-devices
```

You should see:

```
Virtual Camera 1 (platform:v4l2loopback-000):
    /dev/video10

Virtual Camera 2 (platform:v4l2loopback-001):
    /dev/video11

Virtual Camera 3 (platform:v4l2loopback-002):
    /dev/video12
```

### Summary
1. **Create `/etc/modules-load.d/v4l2loopback.conf`** to load `v4l2loopback` automatically at boot.
2. **Create `/etc/modprobe.d/v4l2loopback.conf`** to define the parameters for the virtual cameras.
3. **Update initramfs (optional)**.
4. **Reboot and verify**.

This setup will ensure that your virtual cameras are recreated automatically every time the Raspberry Pi starts, allowing them to be used for various purposes without manual intervention.

## After setting up the virtual cameras, we need to pass the CCTV footage to the virtual camera using ffmpeg. Here's the command to do that:

### Test command to start a Gstream on the CCTV Camera
 ```bash
gst-launch-1.0 rtspsrc location=rtsp://username:password@192.168.1.201:554/stream1 ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink
 ```

  
### Ounce everythig is working as intented you can use the following commandto make the CCTV Camera to a Virtual Display at video10
#### To capature and process the camera feed we need to use a package called motion, follow this repo to setup motion properly https://github.com/apple-fritter/RTSP.to-webcam

Ounce you are done with the motion setup you can use the following command to stream the CCTV camera to the virtual camera:

 ```bash
 ffmpeg -re -i rtsp://username:password@192.168.1.201:554/stream1 -r 30 -f v4l2 -vcodec rawvideo -pix_fmt yuyv422 /dev/video10
 ```
Please note the the -pix_fmt yuyv422 is the format of the virtual camera, you can change it to the format of your virtual camera. This format also needs to be added into the `hailo-rpi5-examples/basic_pipelines/hailo_rpi_common.py` in line number 162-166: 

```python
    elif source_type == 'usb':
        source_element = (
            f'v4l2src device={video_source} name={name} ! '
            'video/x-raw, format=YUY2, width=640, height=360 ! '
        )
```
### If everything is working you will get this outout
 ```bash 
	Input #0, rtsp, from 'rtsp://username:password@192.168.1.201:554/stream1':
	  Metadata:
	    title           : Session streamed by "TP-LINK RTSP Server"
	    comment         : stream2
	  Duration: N/A, start: 0.000000, bitrate: N/A
	  Stream #0:0: Video: h264 (Main), yuv420p(tv, bt709, progressive), 640x360, 15 fps, 16.67 tbr, 90k tbn
	  Stream #0:1: Audio: pcm_alaw, 8000 Hz, mono, s16, 64 kb/s
	Stream mapping:
	  Stream #0:0 -> #0:0 (h264 (native) -> rawvideo (native))
	Press [q] to stop, [?] for help
	Output #0, video4linux2,v4l2, to '/dev/video10':
	  Metadata:
	    title           : Session streamed by "TP-LINK RTSP Server"
	    comment         : stream2
	    encoder         : Lavf59.27.100
	  Stream #0:0: Video: rawvideo (YUY2 / 0x32595559), yuyv422(tv, bt709, progressive), 640x360, q=2-31, 61440 kb/s, 16.67 fps, 16.67 tbn

```
