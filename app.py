from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from rembg import remove

from PIL import Image

import base64
import io

app = Flask(__name__)

CORS(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/remove-bg", methods=["POST"])
def remove_bg():

    try:

        data = request.get_json()

        image_data = data["image"]

        color = data.get("color", "white")

        if "," in image_data:
            image_data = image_data.split(",")[1]

        input_bytes = base64.b64decode(image_data)

        output_bytes = remove(input_bytes)

        img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

        if color == "white":
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))

        elif color == "blue":
            bg = Image.new("RGBA", img.size, (67, 142, 219, 255))

        else:
            bg = Image.new("RGBA", img.size, (255, 255, 255, 0))

        bg.alpha_composite(img)

        buffer = io.BytesIO()

        bg.convert("RGB").save(buffer, format="PNG")

        encoded = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "success": True,
            "image": "data:image/png;base64," + encoded
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)