import glob
import imp
import os
import urllib.request as urllib

import numpy as np
import progressbar
import requests
import sys

import time
from bs4 import BeautifulSoup

ASPECT_RATIO = 16 / 9


def is_open_cv_available() -> bool:
    try:
        imp.find_module('cv2')
        return True
    except ImportError:
        return False


def main():
    r = requests.get('https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss')
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.findAll('item')
    new_images = set()
    for idx, item in enumerate(items[:5]):
        url = item.find('enclosure').get('url')
        title = item.find('title').decode_contents(formatter="html")
        filename = url.split('/')[-1]
        new_images.add(filename)
        desc = item.find('description').decode_contents(formatter="html")
        print('#{}:\n{}\nImage url:{}'.format(idx + 1, desc, url))
        bar = None

        def dl_progress(count, block_size, total_size):
            nonlocal bar
            if bar is None:
                bar = progressbar.ProgressBar(max_value=total_size)
            elif count * block_size < total_size:  # Content length can be incorrect
                bar.update(count * block_size)

        if not os.path.exists(filename):
            urllib.urlretrieve(url, filename, reporthook=dl_progress)
            print("\nFinished")
        else:
            print('Already downloaded!')
            continue

        if is_open_cv_available():
            if 'cv2' not in sys.modules:
                # noinspection PyPackageRequirements
                import cv2
            image = cv2.imread(filename)
            cv2.startWindowThread()
            height, width, channels = image.shape
            if width < height * ASPECT_RATIO:
                target_height = height
                target_width = int(np.round(height * ASPECT_RATIO))
            else:
                continue
            target_image = np.zeros((target_height, target_width, 3), dtype=np.uint8)
            target_image.fill(150)
            big_image_ratio = target_width / width
            background_width = int(width * big_image_ratio)
            background_height = int(height * big_image_ratio)
            background = cv2.resize(image, (background_width, background_height))
            background = background[int(background_height / 2 - target_height / 2):
            int(background_height / 2 + target_height / 2),
                         int(background_width / 2 - target_width / 2):
                         int(background_width / 2 + target_width / 2)]
            background = cv2.GaussianBlur(background, (61, 61), 0)
            target_image = background
            target_image[0:height,
            int(np.floor(target_width / 2 - width / 2)):
            int(np.floor((target_width / 2 + width / 2)))] = image

            cv2.startWindowThread()
            preview_ratio = 200 / target_height
            cv2.imwrite(filename, target_image)
            preview = cv2.resize(target_image, (int(target_width * preview_ratio), int(target_height * preview_ratio)))
            cv2.imshow(title, preview)
            cv2.waitKey(3000)

    all_images = glob.glob('*.jpg')
    to_remove = list(set(all_images) - new_images)
    if len(items) != 0:
        for file in to_remove:
            os.remove(file)
            print('{} removed'.format(file))
    time.sleep(5)


if __name__ == '__main__':
    main()
