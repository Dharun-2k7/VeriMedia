import sys
import os
import glob
sys.path.append('/home/dharun/Desktop/DEEPFAKE_CRYPO/verimedia/backend')
from app.detection.analyzer import analyze_image

files = sorted(glob.glob('/home/dharun/Desktop/DEEPFAKE_CRYPO/verimedia/storage/files/*.jpeg'), key=os.path.getmtime, reverse=True)[:4]

for f in files:
    print(f"Testing {os.path.basename(f)}...")
    with open(f, 'rb') as img_file:
        res = analyze_image(img_file.read())
        print(f"Probability: {res['probability']}")
        for k, v in res['signals'].items():
            print(f"  {k}: {v['score']}")
    print("-" * 40)
