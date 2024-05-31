# Aesthetic Scorer
This is a fork of [https://github.com/Linaqruf/cafe-aesthetic-scorer](https://github.com/Linaqruf/cafe-aesthetic-scorer)

It adds a simple way of using the tool, as well as preview the results.

The tool is meant to rate the image aesthetically, as well as provide some other metadata based on the type of image it is.

# Screenshot
![image](https://github.com/MNeMoNiCuZ/aesthetic-scorer/assets/60541708/d6a3295d-3530-483f-9e8d-a9e750d79b7a)


# Installation
Set up a virtual environment to run the script. Feel free to run the `setup.bat` to automatically set one up.

Install the requirements `pip install -r requirements.txt`. This is optionally done by the setup script.

Install the correct version of [pytorch](https://pytorch.org/) for your CUDA. It's usually:

`pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

or

`pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`

# Using the tool

1. Place the images or folders of images in the /input/ directory.
2. Run `1-rate.bat`
3. Run `2-view.bat`

Alternatively:


1. Place the images or folders of images in the /input/ directory.
2. Activate your environment and run `rate.py`.
3. Launch a web server: `python -m http.server 8000` and open [`http://localhost:8000/index.html`](http://localhost:8000/index.html) in your web browser.
