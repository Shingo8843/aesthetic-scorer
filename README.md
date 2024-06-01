# Aesthetic Scorer
This is a fork of [https://github.com/Linaqruf/cafe-aesthetic-scorer](https://github.com/Linaqruf/cafe-aesthetic-scorer)

It adds a simple way of using the tool, as well as preview the results.

The tool is meant to rate the image aesthetically, as well as provide some other metadata based on the type of image it is.

# Screenshot
![image](https://github.com/MNeMoNiCuZ/aesthetic-scorer/assets/60541708/449fadf1-3567-4ff9-8a90-22a7faea4207)




# Installation
Set up a virtual environment to run the script. Feel free to run the `setup.bat` to automatically set one up.

Install the requirements `pip install -r requirements.txt`. This is optionally done by the setup script.

Install the correct version of [pytorch](https://pytorch.org/) for your CUDA. It's usually:

`pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

or

`pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`

# Using the tool

1. Place the images or folders of images in the /input/ directory.
2. Run `1-rate.bat` to rate the images with the system.

You can now view the images and their rating as a website:

3. Run `2-view.bat` to launch the server and website.

On the website, you can expand the arrow below the title to show the options.

![image](https://github.com/MNeMoNiCuZ/aesthetic-scorer/assets/60541708/eae495a6-655f-443c-9abd-272f661ba63e)

4. From the options, you can set the gallery column count, width and sorting options.
5. You can also play with the filter/pruning settings. Use > or < and integers as % to set the filter values
>  Example: Aesthetics >50 will keep only images that are rated at 0.5 or higher in aesthetics
6. By pressing the `Prune`-button, the pruning script will move any currently hidden images to a `pruned` directory, along with a json containing the pruned images data.
>  You can also do this by running  the `3-prune.bat` script. This will use the `pruneconfig.ini` as the pruning settings.

Alternatively:

1. Place the images or folders of images in the /input/ directory.
2. Activate your environment and run `rate.py`.
3. (Optional) Launch a web server: `python -m http.server 8000` and open [`http://localhost:8000/index.html`](http://localhost:8000/index.html) in your web browser.
4. Edit `pruneconfig.ini` with your pruning preferences (using < and > and full integers as %-values).
5. Run `prune.py`.


# Known Issues
- [ ] The realistic value isn't properly being sorted with the drop-down menu (therefore commented out)

# Todo
- [ ] Add a "Clear" button to the left side of the filters on the webui
