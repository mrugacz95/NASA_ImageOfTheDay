# NASA Image of the day downloader
Python script to download latest daily images from NASA
##### Installation 
1. Install OpenCV for python:
```
conda install -c menpo opencv3 
```
2. Install requirements:
```
pip install -r requirements.txt
```
##### Usage
```
python get_images.py
```
##### Result
Script will download and display last 5 photos from NASA image of the day.
##### Configuration for desktop slide show
You can add this directory for slide show. 
On Windows if you want to download images on every startup add `get_images.bat` to autostart (`CTRL+R` -> `shell:startup`).
