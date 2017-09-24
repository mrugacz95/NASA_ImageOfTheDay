import glob
import os
import urllib.request as urllib

import cv2
import numpy as np
import progressbar
import requests
from bs4 import BeautifulSoup

ASPECT_RATIO = 16 / 9


def main():

    r = requests.get('https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss')
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.findAll('item')
    new_images = set()
    cv2.startWindowThread()
    for idx, item in enumerate(items[:5]):
        url = item.find('enclosure').get('url')
        title = item.find('title').decode_contents(formatter="html")
        filename = url.split('/')[-1]
        new_images.add(filename)
        desc = item.find('description').decode_contents(formatter="html")
        print('#{}:\n{}\nImage url:{}'.format(idx, desc, url))
        bar = None

        def dl_progress(count, block_size, total_size):
            nonlocal bar
            if bar is None:
                bar = progressbar.ProgressBar(max_value=total_size)
            elif count * block_size < total_size:  # Content length can be incorrect
                bar.update(count * block_size)

        if not os.path.exists(filename):
            urllib.urlretrieve(url, filename, reporthook=dl_progress)
            print("Finished")
        else:
            print('Already downloaded!')
            continue
        image = cv2.imread(filename)

        height, width, channels = image.shape
        if width < height * ASPECT_RATIO:
            target_height = height
            target_width = int(np.round(height * ASPECT_RATIO))
        else:
            target_height = int(np.round(width / ASPECT_RATIO))
            target_width = width
        target_image = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        target_image.fill(150)
        if width < height * ASPECT_RATIO:
            big_image_ratio = target_width / width
        else:
            big_image_ratio = target_height / height
        background_width = int(width * big_image_ratio)
        background_height = int(height * big_image_ratio)
        background = cv2.resize(image, (background_width, background_height))
        background = background[int(background_height / 2 - target_height / 2):
                                int(background_height / 2 + target_height / 2),
                                int(background_width / 2 - target_width / 2):
                                int(background_width / 2 + target_width / 2)]
        background = cv2.GaussianBlur(background, (61, 61), 0)
        target_image = background
        if width < height * ASPECT_RATIO:
            target_image[0:height,
                         int(np.floor(target_width / 2 - width / 2)):
                         int(np.floor((target_width / 2 + width / 2)))] = image
        else:
            target_image[int(np.floor(target_height / 2 - height / 2)):
                         int(np.floor((target_height / 2 + height / 2))),
                         0:width] = image

        cv2.startWindowThread()
        preview_ratio = 200 / target_height
        cv2.imwrite(filename, target_image)
        preview = cv2.resize(target_image, (int(target_width * preview_ratio), int(target_height * preview_ratio)))
        cv2.imshow(title, preview)
        cv2.waitKey(3000)

    all_images = glob.glob('*.jpg')
    to_remove = list(set(all_images) - new_images)
    for file in to_remove:
        os.remove(file)
        print('{} removed'.format(file))


if __name__ == '__main__':
    main()
