import json
import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from tqdm import tqdm
from transformers import pipeline
import argparse

# Define default values for certain variables
DEFAULT_MAX_WORKERS = 4
DEFAULT_BATCH_SIZE = 3
DEFAULT_INPUT_DIR = "./input"
DEFAULT_OUTPUT_DIR = "./output/results.json"

# Create the argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument("--batch_size", type=int, default=DEFAULT_BATCH_SIZE, help="Batch size for image classification")
parser.add_argument("--use_gpu", action="store_true", help="Use GPU for image classification")
parser.add_argument("--img_dir", type=str, default=DEFAULT_INPUT_DIR, help="Path to the directory containing images")
parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR, help="Path to the output JSON file")
parser.add_argument("--max_workers", type=int, default=DEFAULT_MAX_WORKERS, help="Maximum number of worker threads to use in the thread pool")

# Parse the arguments
args = parser.parse_args()

# Get the values of the arguments
batch_size = args.batch_size
use_gpu = args.use_gpu
img_dir = args.img_dir
output_dir = args.output_dir
max_workers = args.max_workers

# Create a list to store the results for each image
results = []

# Create a cache to store the results of the classification tasks
cache = {}

# Function to process images recursively
def process_images_recursively(input_dir):
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
                input_img_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_img_path, input_dir)
                
                input_img = Image.open(input_img_path)

                # Use the aesthetic classifier
                data = pipe_aesthetic(input_img, top_k=2)
                final = {d["label"]: d["score"] for d in data}

                # Use the style classifier
                data = pipe_style(input_img, top_k=5)
                final_style = {d["label"]: d["score"] for d in data}

                # Use the waifu classifier
                data = pipe_waifu(input_img, top_k=5)
                final_waifu = {d["label"]: d["score"] for d in data}

                # Store the results for this image in the cache
                result = {"filename": relative_path.replace(os.sep, "/"), "aesthetic": final, "style": final_style, "waifu": final_waifu}
                results.append(result)
                cache[file] = result

# Create a thread pool with the specified number of worker threads
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    if use_gpu:
        # Use the GPU for image classification
        device = 0
    else:
        # Use the CPU for image classification
        device = -1

    pipe_aesthetic = pipeline("image-classification", "cafeai/cafe_aesthetic", device=device, batch_size=batch_size)
    pipe_style = pipeline("image-classification", "cafeai/cafe_style", device=device, batch_size=batch_size)
    pipe_waifu = pipeline("image-classification", "cafeai/cafe_waifu", device=device, batch_size=batch_size)

    # Process images recursively
    process_images_recursively(img_dir)

    # Save the results to a JSON file
    with open(output_dir, "w") as f:
        json.dump(results, f, indent=2)
