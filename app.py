import os
import io
from flask import Flask, request, render_template, send_file, send_from_directory
from rembg import remove

app = Flask(__name__)

# 1. Main Home Page Route
@app.route('/')
def home():
    return render_template('index.html')

# 2. Serves ads.txt from root directory
@app.route('/ads.txt')
def ads_txt():
    return send_from_directory(app.root_path, 'ads.txt')

# 3. Image Background Removal Processing Route
@app.route('/process', methods=['POST'])
def process():
    file = request.files.get('image')
    if not file:
        return "No image provided", 400
    
    input_data = file.read()
    output_data = remove(input_data)
    
    return send_file(
        io.BytesIO(output_data), 
        mimetype='image/png',
        as_attachment=True,
        download_name='bg_removed.png'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)