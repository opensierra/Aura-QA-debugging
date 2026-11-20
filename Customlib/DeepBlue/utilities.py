import time
from datetime import datetime
from .config import CF_LEVEL

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")

def format_ocr(ocr_result):
    t0 = time.time()
    t = t0
    
    log("Formating OCR regions...")
    regions = []
    
    if not ocr_result or len(ocr_result) == 0 or "rec_texts" not in ocr_result[0]:
        log("Error: Formato de OCR result inválido")
        return []
    
    for i, (text, score) in enumerate(zip(ocr_result[0]["rec_texts"], ocr_result[0]["rec_scores"])):
        box = ocr_result[0]["rec_boxes"][i]
        x1, y1, x2, y2 = (int(v) for v in box)
        
        regions.append({
            "id": i,
            "text": text,
            "bbox": {
                "x": x1, 
                "y": y1, 
                "width": x2 - x1, 
                "height": y2 - y1
            },
            "score": round(float(score), 3),
            "ctx": score < (1 - CF_LEVEL),
        })
    
    log(f"      [OK] {len(regions)} regiones extraidas")
    log(f"      Duration: {time.time()-t:.2f}s")
    
    return regions