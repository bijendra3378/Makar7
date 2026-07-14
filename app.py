from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from PIL import Image

import base64
import io

app = Flask(__name__)

CORS(app)

# rembg (and its ~50-100MB ONNX model) is imported lazily inside remove_bg(),
# not at module load time. This keeps app startup fast so Render's health
# check doesn't time out while the model is downloading/loading. The model
# is only pulled in the first time someone actually uses AI background removal.
_remove_fn = None


def get_remove_fn():
    global _remove_fn
    if _remove_fn is None:
        from rembg import remove
        _remove_fn = remove
    return _remove_fn


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    # Lightweight endpoint for Render's health checks - does not touch rembg
    return jsonify({"status": "ok"})


@app.route("/remove-bg", methods=["POST"])
def remove_bg():

    try:

        data = request.get_json(silent=True)

        if not data or "image" not in data:
            return jsonify({
                "success": False,
                "message": "No image provided"
            }), 400

        image_data = data["image"]

        color = data.get("color", "white")

        if "," in image_data:
            image_data = image_data.split(",")[1]

        input_bytes = base64.b64decode(image_data)

        remove = get_remove_fn()
        output_bytes = remove(input_bytes)

        img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

        if color == "white":
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            bg.alpha_composite(img)
            final_img = bg.convert("RGB")

        elif color == "blue":
            bg = Image.new("RGBA", img.size, (67, 142, 219, 255))
            bg.alpha_composite(img)
            final_img = bg.convert("RGB")

        else:
            # Keep true transparency instead of flattening to black
            final_img = img

        buffer = io.BytesIO()

        final_img.save(buffer, format="PNG")

        encoded = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "success": True,
            "image": "data:image/png;base64," + encoded
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)