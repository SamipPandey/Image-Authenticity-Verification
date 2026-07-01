from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import analyze_image

app = Flask(__name__)
CORS(app) 

# --- ADD THIS PART ---
@app.route('/', methods=['GET'])
def home():
    return "<h1>Image Verification Backend is Running!</h1><p>The extension will connect here automatically.</p>"
# ---------------------

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    url = data.get('image_url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    report = analyze_image(url)
    return jsonify(report)

if __name__ == '__main__':
    # Using 0.0.0.0 makes it easier for the browser to find
    app.run(host='0.0.0.0', port=5000, debug=True)