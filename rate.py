import json
import os
from PIL import Image
from tqdm import tqdm
from transformers import pipeline
import argparse
import warnings
import torch
from datasets import Dataset, Image as DatasetImage

# Suppress FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)

# Define default values for certain variables
DEFAULT_MAX_WORKERS = 4
DEFAULT_BATCH_SIZE = 3
DEFAULT_INPUT_DIR = "./input"
DEFAULT_OUTPUT_DIR = "./output/results.json"
DEFAULT_USE_GPU = True
DEFAULT_USE_DATASET = False

# Create the argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument("--batch_size", type=int, default=DEFAULT_BATCH_SIZE, help="Batch size for image classification")
parser.add_argument("--use_gpu", type=bool, default=DEFAULT_USE_GPU, help="Use GPU for image classification")
parser.add_argument("--img_dir", type=str, default=DEFAULT_INPUT_DIR, help="Path to the directory containing images")
parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR, help="Path to the output JSON file")
parser.add_argument("--max_workers", type=int, default=DEFAULT_MAX_WORKERS, help="Maximum number of worker threads to use in the thread pool")
parser.add_argument("--use_dataset", type=bool, default=DEFAULT_USE_DATASET, help="Use dataset for batch processing (set to False if the process gets stuck)")

# Parse the arguments
args = parser.parse_args()

# Get the values of the arguments
batch_size = args.batch_size
use_gpu = args.use_gpu
img_dir = args.img_dir
output_dir = args.output_dir
max_workers = args.max_workers
use_dataset = args.use_dataset

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_dir), exist_ok=True)

# Create a list to store the results for each image
results = []

# Create a cache to store the results of the classification tasks
cache = {}

# Function to get image paths recursively
def get_image_paths(input_dir):
    image_paths = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
                image_paths.append(os.path.join(root, file))
    return image_paths

# Check GPU availability and print detailed information
if use_gpu:
    if torch.cuda.is_available():
        device = 0
        print("GPU is available. Using GPU for image classification.")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Available GPUs: {torch.cuda.device_count()}")
        print(f"Current GPU device: {torch.cuda.current_device()}")
        print(f"GPU device name: {torch.cuda.get_device_name(device)}")
    else:
        device = -1
        print("GPU is not available. Falling back to CPU for image classification.")
        print("Detailed CUDA information:")
        print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")
        print(f"torch.cuda.device_count(): {torch.cuda.device_count()}")
        print(f"torch.version.cuda: {torch.version.cuda}")
else:
    device = -1
    print("Using CPU for image classification.")

# Create the image classification pipelines
pipe_aesthetic = pipeline("image-classification", "cafeai/cafe_aesthetic", device=device, batch_size=batch_size)
pipe_style = pipeline("image-classification", "cafeai/cafe_style", device=device, batch_size=batch_size)
pipe_waifu = pipeline("image-classification", "cafeai/cafe_waifu", device=device, batch_size=batch_size)

# Get the list of image paths
image_paths = get_image_paths(img_dir)
print(f"\n\nFound {len(image_paths)} images to process.")

if use_dataset:
    print("Creating dataset map.\nIf the process gets stuck, try disabling the dataset mapping.\n Do this in rate.py by setting 'DEFAULT_USE_DATASET' to false or by using the argument '--use_dataset=False.'")
else:
    print("Dataset mapping is disabled. This can be enabled in 'rate.py' for optimized performance.")

def process_image(img_path):
    try:
        input_img = Image.open(img_path).convert("RGB")

        # Use the aesthetic classifier
        data = pipe_aesthetic(input_img, top_k=2)
        final = {d["label"]: d["score"] for d in data}

        # Use the style classifier
        data = pipe_style(input_img, top_k=5)
        final_style = {d["label"]: d["score"] for d in data}

        # Use the waifu classifier
        data = pipe_waifu(input_img, top_k=5)
        final_waifu = {d["label"]: d["score"] for d in data}

        # Store the results for this image
        relative_path = os.path.relpath(img_path, img_dir)
        result = {"filename": relative_path.replace(os.sep, "/"), "aesthetic": final, "style": final_style, "waifu": final_waifu}
        results.append(result)
        cache[os.path.basename(img_path)] = result
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")

if use_dataset:
    # Create a dataset from the image paths
    dataset = Dataset.from_dict({"image_path": image_paths})
    
    # Function to open and process images
    def open_image(x):
        try:
            image = Image.open(x["image_path"]).convert("RGB")
            return {"image": image, "path": x["image_path"]}
        except Exception as e:
            print(f"Error opening image {x['image_path']}: {e}")
            return {"image": None, "path": x["image_path"]}

    # Map the open_image function to the dataset
    dataset = dataset.map(open_image, remove_columns=["image_path"])

    def process_batch(batch):
        batch_results = []
        for input_img, img_path in zip(batch["image"], batch["path"]):
            if input_img is None:
                continue

            # Use the aesthetic classifier
            data = pipe_aesthetic(input_img, top_k=2)
            final = {d["label"]: d["score"] for d in data}

            # Use the style classifier
            data = pipe_style(input_img, top_k=5)
            final_style = {d["label"]: d["score"] for d in data}

            # Use the waifu classifier
            data = pipe_waifu(input_img, top_k=5)
            final_waifu = {d["label"]: d["score"] for d in data}

            # Store the results for this image
            relative_path = os.path.relpath(img_path, img_dir)
            result = {"filename": relative_path.replace(os.sep, "/"), "aesthetic": final, "style": final_style, "waifu": final_waifu}
            batch_results.append(result)
            cache[os.path.basename(img_path)] = result
        
        return {"results": batch_results}

    # Process images using the dataset and pipelines in batches
    try:
        dataset = dataset.map(process_batch, batched=True, batch_size=batch_size)

        # Save the results to a JSON file
        results = [item for sublist in dataset["results"] for item in sublist]
        with open(output_dir, "w") as f:
            json.dump(results, f, indent=2)
        print("Results successfully saved to", output_dir)

    except Exception as e:
        print("An error occurred:", str(e))

else:
    try:
        for img_path in tqdm(image_paths, desc="Processing images"):
            process_image(img_path)

        # Save the results to a JSON file
        with open(output_dir, "w") as f:
            json.dump(results, f, indent=2)
        print("Results successfully saved to", output_dir)

    except Exception as e:
        print("An error occurred:", str(e))

print("Processing complete.")