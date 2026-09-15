import random
from typing import Dict, Any

def analyze_media(file_bytes: bytes, file_type: str) -> Dict[str, Any]:
    """
    DEMO AI Detector.
    Returns simulated manipulation probabilities.
    In a real system, this would load a PyTorch/TensorFlow model or call an external API.
    """
    
    # We use the file size to seed the random generator for consistent demo results 
    # per identical file, so that the Tamper Test works predictably.
    random.seed(len(file_bytes))
    
    probability = round(random.uniform(0.01, 0.95), 2)
    
    # For Tamper Test demo: if file size is artificially modified (e.g., small crop)
    # the probability will change. If we want a specific result based on file size,
    # we can hardcode some logic, but random seed is fine.
    
    if probability < 0.3:
        assessment = "LOW LIKELIHOOD"
    elif probability < 0.7:
        assessment = "SUSPICIOUS"
    else:
        assessment = "HIGH LIKELIHOOD"
        
    result = {
        "manipulation_probability": int(probability * 100),
        "assessment": assessment
    }
    
    if file_type.startswith("video"):
        result["frames_analyzed"] = random.randint(150, 300)
        result["suspicious_frames"] = int(result["frames_analyzed"] * probability)
        result["average_probability"] = int(probability * 100)
        result["maximum_probability"] = min(100, int((probability + 0.1) * 100))
        
    return result
