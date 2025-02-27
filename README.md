# Qualcomm Platform Model Conversion Flask Application

## Requirements
* x86 Computer
* Ubuntu 22.04

## Supported Models
* YOLOv8
* YOLOv11
* YOLOv12
* DETR

## Environment Setup
```
git clone https://github.com/Kaiwei0323/qc_model_conversion_flask.git
cd qc_model_conversion_flask
```
Modify line 39 in the code to specify the desired host IP and port.
Then, build and run the application using Docker:
```
sudo docker build -t flask-snpe-app .
sudo docker run -p 5000:5000 --network=host --rm flask-snpe-app
```
The application will be accessible on the configured IP and port.

## Application User Manual

### Model Conversion Tab
#### For YOLOv8, YOLOv11, YOLOv12:
⚠ **Caution**: for yolo model please export model with **op=10**
1. Upload your ONNX model.
2. Select "Yes" for using an encoding file.
3. Upload yolo8_act.encodings.
4. Select "Yes" to enable quantization.
5. Choose 640x640 for resolution.
6. Upload your image files.
7. Press the Convert button.

#### For DETR:

1. Upload your ONNX model.
2. Select "No" for using an encoding file.
3. Select "Yes" to enable quantization.
4. Choose 480x480 for resolution.
5. Upload your image files.
6. Press the Convert button.

### Model Visualization Tab
1. Upload your DLC model.
2. Press the Visualize button.
