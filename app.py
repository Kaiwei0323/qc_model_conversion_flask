import sys
import os
import subprocess
from flask import Flask, request, render_template, send_from_directory, redirect, url_for

app = Flask(__name__)

# Define folders for uploads, DLC models, and quantization data
UPLOAD_FOLDER = 'uploads'
DLC_FOLDER = 'dlc'
QUANTIZE_FOLDER = 'quantization_data'

# Ensure necessary directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DLC_FOLDER, exist_ok=True)
os.makedirs(QUANTIZE_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/convert', methods=['GET', 'POST'])
def convert_model():
    if request.method == 'POST':
        if 'file' not in request.files or 'quantize' not in request.form or 'encoding' not in request.form:
            return 'Missing file or selection', 400
        
        file = request.files['file']
        quantize = request.form['quantize']  # 'yes' or 'no'
        encoding = request.form['encoding']  # 'yes' or 'no'
        resolution = request.form.get('resolution', '640')  # Default to 640
        
        if file.filename == '':
            return 'No selected file', 400
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        base_name = os.path.splitext(file.filename)[0]
        dlc_files = []

        # Check if encoding is enabled
        if encoding == 'yes':
            if 'encodings_file' not in request.files:
                return 'Encoding file required', 400
            encodings_file = request.files['encodings_file']
            if encodings_file.filename == '':
                return 'No encoding file selected', 400
            
            encodings_path = os.path.join(UPLOAD_FOLDER, encodings_file.filename)
            encodings_file.save(encodings_path)
            
            # Convert ONNX to fp32 DLC with encoding
            fp32_encoded_dlc = os.path.join(DLC_FOLDER, f"{base_name}_encode_fp32.dlc")
            command_fp32 = [
                'snpe-onnx-to-dlc',
                '--input_network', filepath,
                '--quantization_overrides', encodings_path,
                '--output_path', fp32_encoded_dlc
            ]
        else:
            # Convert ONNX to standard fp32 DLC
            fp32_dlc = os.path.join(DLC_FOLDER, f"{base_name}_fp32.dlc")
            command_fp32 = [
                'snpe-onnx-to-dlc',
                '--input_network', filepath,
                '--output_path', fp32_dlc
            ]
        
        # Run the conversion command
        try:
            subprocess.run(command_fp32, check=True)
            dlc_files.append(os.path.basename(fp32_encoded_dlc) if encoding == 'yes' else os.path.basename(fp32_dlc))
        except subprocess.CalledProcessError as e:
            return f'Error during FP32 conversion: {str(e)}', 500

        # Handle quantization if enabled
        if quantize == 'yes':
            quantize_images = request.files.getlist('quantize_images')
            if not quantize_images:
                return 'No quantization images uploaded', 400

            selected_folder_name = os.path.dirname(quantize_images[0].filename) or "default"
            image_folder = os.path.join(QUANTIZE_FOLDER, f"{selected_folder_name}_{resolution}")
            os.makedirs(image_folder, exist_ok=True)

            for image in quantize_images:
                image_path = os.path.join(image_folder, os.path.basename(image.filename))
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                image.save(image_path)

            # Define script paths correctly
            raw_script = os.path.join(os.path.dirname(__file__), 'create_inceptionv3_raws.py')
            list_script = os.path.join(os.path.dirname(__file__), 'create_file_list.py')

            # Generate RAW images
            command_raw = ['python', raw_script, '-s', resolution, '-i', image_folder, '-d', image_folder]
            try:
                subprocess.run(command_raw, check=True)
            except subprocess.CalledProcessError as e:
                return f'Error processing raw images: {str(e)}', 500

            # Generate image file list
            list_txt = os.path.join(image_folder, 'image_file_list.txt')
            command_list = ['python', list_script, '-i', image_folder, '-o', list_txt, '-e', '*.raw']
            try:
                subprocess.run(command_list, check=True)
            except subprocess.CalledProcessError as e:
                return f'Error creating file list: {str(e)}', 500

            # Perform DLC quantization
            if encoding == 'yes':
                int8_dlc = os.path.join(DLC_FOLDER, f"{base_name}_encode_int8.dlc")
                command_quantize = [
                    'snpe-dlc-quantize',
                    '--input_dlc', fp32_encoded_dlc,
                    '--override_params',
                    '--input_list', list_txt,
                    '--output_dlc', int8_dlc
                ]
            else:
                int8_dlc = os.path.join(DLC_FOLDER, f"{base_name}_int8.dlc")
                command_quantize = [
                    'snpe-dlc-quantize',
                    '--input_dlc', fp32_dlc,
                    '--input_list', list_txt,
                    '--output_dlc', int8_dlc
                ]

            try:
                subprocess.run(command_quantize, check=True)
                dlc_files.append(os.path.basename(int8_dlc)) 
            except subprocess.CalledProcessError as e:
                return f'Error during quantization: {str(e)}', 500
               

        # return render_template('download.html', filenames=dlc_files)
        return redirect(url_for('download_page', filenames=','.join(dlc_files)))
    
    return render_template('convert.html')

@app.route('/download')
def download_page():
    filenames = request.args.get('filenames', '').split(',')
    return render_template('download.html', filenames=filenames)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DLC_FOLDER, filename)
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")  # Debugging
        return 'File not found', 404
    print(f"✅ Serving file: {file_path}")  # Debugging
    return send_from_directory(DLC_FOLDER, filename, as_attachment=True)

@app.route('/visualization', methods=['GET', 'POST'])
def visualize_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        
        filepath = os.path.join(DLC_FOLDER, file.filename)
        file.save(filepath)
        
        return redirect(url_for('visualize_specific_file', filename=file.filename))

    return render_template('visualization.html', filename=None, output=None)
    
@app.route('/visualization/<filename>')
def visualize_specific_file(filename):
    file_path = os.path.join(DLC_FOLDER, filename)
    if not os.path.exists(file_path):
        return 'File not found', 404
    
    command = ['snpe-dlc-info', '-i', file_path]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        output = f'Error during visualization: {str(e)}'
    
    return render_template('visualization.html', filename=filename, output=output)

if __name__ == "__main__":
    # Default values
    host = "0.0.0.0"
    port = 5000
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if "--host=" in arg:
                host = arg.split("=")[1]
            if "--port=" in arg:
                port = int(arg.split("=")[1])

    app.run(host=host, port=port, debug=True)


