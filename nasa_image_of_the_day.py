import glob
import urllib.request as urllib

import requests
from bs4 import BeautifulSoup
import progressbar
import os.path
import importlib

def main():
    r = requests.get('https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss')
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.findAll('item')
    new_images = set()
    for idx, item in enumerate(items[:5]):
        url = item.find('enclosure').get('url')
        filename = url.split('/')[-1]
        new_images.add(filename)
        desc = item.find('description').decode_contents(formatter="html")
        print('#{}:\n{} Image url:{}'.format(idx, desc, url))
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
        try:
            import cv2
            img = cv2.imread(filename)
            height, width, channels = img.shape
            ratio = 200 / height
            img = cv2.resize(img, (int(width * ratio), int(height * ratio)))
            wndName = '{}'.format(filename)
            cv2.imshow(wndName, img)
            cv2.moveWindow(wndName, 200, 200)
            cv2.waitKey(3000)
        except ImportError:
            print('OpenCV not found, preview not available')
    all_images = glob.glob('*.jpg')
    to_remove = list(set(all_images) - new_images)
    for file in to_remove:
        os.remove(file)
        print('{} removed'.format(file))


if __name__ == '__main__':
    main()
