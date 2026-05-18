import os
import gdown

FILE_ID = "1RRyX1--zjkvrO_P6lxqpNb5j9tu-dyGM"
OUTPUT_PATH = "ml_models/yield_model.pkl"

os.makedirs("ml_models", exist_ok=True)

if not os.path.exists(OUTPUT_PATH):
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    gdown.download(url, OUTPUT_PATH, quiet=False)