import io
import json
import os

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from PIL.ExifTags import TAGS


SIGHTENGINE_API_USER = os.environ.get("SIGHTENGINE_API_USER", "")
SIGHTENGINE_API_SECRET = os.environ.get("SIGHTENGINE_API_SECRET", "")
SIGHTENGINE_URL = "https://api.sightengine.com/1.0/check.json"


def extract_metadata(pil_image):
    """Pulls whatever EXIF tags exist. Most web-downloaded images have none
    (social media strips it), which is itself a useful signal."""
    exif_data = {}
    try:
        raw_exif = pil_image.getexif()
        if raw_exif:
            for tag_id, value in raw_exif.items():
                tag = TAGS.get(tag_id, tag_id)
                try:
                    json.dumps(value)
                    exif_data[str(tag)] = value
                except (TypeError, ValueError):
                    exif_data[str(tag)] = str(value)
    except Exception:
        pass

    return {
        "found": len(exif_data) > 0,
        "tags": exif_data,
        "format": pil_image.format,
        "size": pil_image.size,
    }


def real_ai_detection(image_bytes):

    if not SIGHTENGINE_API_USER or not SIGHTENGINE_API_SECRET:
        return None

    try:
        files = {"media": ("image.jpg", image_bytes)}
        params = {
            "models": "genai",
            "api_user": SIGHTENGINE_API_USER,
            "api_secret": SIGHTENGINE_API_SECRET,
        }
        response = requests.post(SIGHTENGINE_URL, files=files, data=params, timeout=15)
        data = response.json()

        if data.get("status") != "success":
            return None

        ai_probability = data["type"]["ai_generated"]  # 0.0 - 1.0

        return {
            "ai_likelihood_percent": round(ai_probability * 100, 1),
            "method": "sightengine_genai_api (real detector)",
        }
    except Exception:
        return None


def guess_ai_generated(pil_image):
 
    small = pil_image.convert("L").resize((128, 128))
    pixels = list(small.getdata())
    mean = sum(pixels) / len(pixels)
    variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)

    if variance < 200:
        likelihood = 85
    elif variance < 800:
        likelihood = 55
    else:
        likelihood = 20

    return {
        "ai_likelihood_percent": likelihood,
        "method": "pixel_variance_fallback (real detector unavailable or not configured)",
    }


def check_c2pa(pil_image):
 

    return {"found": False, "note": "C2PA check not implemented in this MVP"}


def compute_trust_score(metadata, ai_result, c2pa_result):
    """Very simple weighted score. Higher score = more trustworthy/real."""
    score = 100

    if ai_result["ai_likelihood_percent"] > 70:
        score -= 50
    elif ai_result["ai_likelihood_percent"] > 40:
        score -= 25

    if not metadata["found"]:
        score -= 20

    if not c2pa_result["found"]:
        score -= 10

    score = max(0, min(100, score))

    if score >= 70:
        verdict = "Likely Authentic"
    elif score >= 40:
        verdict = "Uncertain"
    else:
        verdict = "Likely AI-Generated or Manipulated"

    return {"score": score, "verdict": verdict}


@csrf_exempt
def verify_image(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST an image file with field name 'image'"}, status=405)

    if "image" not in request.FILES:
        return JsonResponse({"error": "No file uploaded. Use form field name 'image'."}, status=400)

    uploaded_file = request.FILES["image"]
    image_bytes = uploaded_file.read()

    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
        pil_image.load()
    except Exception:
        return JsonResponse({"error": "Could not read this file as an image."}, status=400)

    metadata = extract_metadata(pil_image)
    ai_result = real_ai_detection(image_bytes) or guess_ai_generated(pil_image)
    c2pa_result = check_c2pa(pil_image)
    trust = compute_trust_score(metadata, ai_result, c2pa_result)

    return JsonResponse({
        "metadata": metadata,
        "ai_detection": ai_result,
        "c2pa": c2pa_result,
        "trust_score": trust,
    })


def health_check(request):
    return JsonResponse({"status": "ok"})
