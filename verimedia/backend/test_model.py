from transformers import pipeline
import sys

print("Loading model...")
pipe = pipeline("image-classification", model="dima806/deepfake_vs_real_image_detection", device="cpu")
print(pipe.model.config.id2label)
