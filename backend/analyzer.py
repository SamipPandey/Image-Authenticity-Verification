import requests
from PIL import Image
from PIL.ExifTags import TAGS
import io

def analyze_image(image_url):
    try:
        response = requests.get(image_url, timeout=5)
        img_bytes = response.content
        img = Image.open(io.BytesIO(img_bytes))
        
        # 1. Metadata Analysis
        exif_data = img._getexif()
        has_metadata = exif_data is not None
        
        # 2. Mock AI Detection (In real life, call Hive AI or similar API here)
        # For MVP, we simulate a check based on common patterns
        ai_prob = 82 if not has_metadata else 15
        
        # 3. Mock C2PA Check
        c2pa_found = "Not Found" # Requires 'c2pa-python' library and specific headers
        
        # 4. Logic for Confidence Score
        score = 100 - ai_prob
        
        verdict = "Highly Suspicious" if score < 40 else "Likely Authentic"

        return {
            "confidence_score": score,
            "ai_likelihood": ai_prob,
            "metadata_found": has_metadata,
            "c2pa_status": c2pa_found,
            "verdict": verdict
        }
    except Exception as e:
        return {"error": str(e)}