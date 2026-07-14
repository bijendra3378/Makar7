import base64
import io
from flask import Flask, request, jsonify, render_template
from PIL import Image
from rembg import remove, new_session

app = Flask(__name__, template_folder="templates")

# Render Free Tier (512MB RAM) को क्रैश से बचाने के लिए 4MB का 'u2netp' लाइटवेट मॉडल
model_session = new_session("u2netp")

@app.route("/")
def index():
    # यह templates/index.html को रेंडर करेगा
    return render_template("index.html")

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"success": False, "message": "No image data provided"}), 400

        image_data = data["image"]
        target_color = data.get("color", "original")

        # Base64 string से हेडर साफ करना (e.g. data:image/png;base64,)
        if "," in image_data:
            header, image_data = image_data.split(",", 1)

        # Base64 को इमेज बाइट्स में बदलना
        img_bytes = base64.b64decode(image_data)
        input_image = Image.open(io.BytesIO(img_bytes))

        # AI मॉडल का इस्तेमाल करके बैकग्राउंड हटाना
        output_image = remove(input_image, session=model_session)

        # अगर यूजर ने White या Blue बैकग्राउंड सिलेक्ट किया है
        if target_color in ["white", "blue"]:
            if target_color == "white":
                bg_color = (255, 255, 255, 255)  # Pure White
            else:
                bg_color = (0, 112, 192, 255)    # Royal Passport Blue

            # सॉलिड बैकग्राउंड इमेज बनाना
            solid_bg = Image.new("RGBA", output_image.size, bg_color)
            # ट्रांसपेरेंट इमेज को सॉलिड बैकग्राउंड के ऊपर मर्ज करना
            final_image = Image.alpha_composite(solid_bg, output_image.convert("RGBA"))
        else:
            final_image = output_image

        # वापस Base64 में कन्वर्ट करना ताकि फ्रंटएंड पर भेजा जा सके
        buffered = io.BytesIO()
        final_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return jsonify({
            "success": True,
            "image": f"data:image/png;base64,{img_str}"
        })

    except Exception as e:
        print("Error processing image:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)