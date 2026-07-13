base64
import io
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from rembg import remove
from PIL import Image

app = Flask(__name__)
# CORS enabled kiya gaya hai taaki GitHub Pages se request bina error ke receive ho sake
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({"success": False, "message": "No image data provided"}), 400

        image_data = data.get('image')
        color_choice = data.get('color', 'white')

        # Base64 string se raw data alag karna
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        # Image bytes ko open karna PIL Object ke roop me
        input_image = Image.open(io.BytesIO(image_bytes))

        # rembg model ki sahayata se background delete karna
        output_transparent = remove(input_image)

        # Dropdown input ke anusar passport color set karna
        if color_choice == 'blue':
            bg_color = (16, 36, 71, 255) # Official Passport Blue
        else:
            bg_color = (255, 255, 255, 255) # Pure Passport White

        # Naya background background canvas banana
        new_background = Image.new("RGBA", output_transparent.size, bg_color)
        new_background.paste(output_transparent, (0, 0), output_transparent)

        # Final conversion to RGB format
        final_image = new_background.convert("RGB")

        # Image ko wapas Base64 Base64 string me stream karna
        buffered = io.BytesIO()
        final_image.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return jsonify({
            "success": True,
            "image": f"data:image/jpeg;base64,{img_str}"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)