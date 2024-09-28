# -*- coding: utf-8 -*-


# system libraries
import re
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# third party libraries
import numpy as np
import cv2
import uuid

# data
from data import global_vars

# path
app_path = global_vars.APP_PATH

#classifier_path = os.path.join(app_path, "custom_libs/haarcascade_frontalface_default.xml")
#FACE_CASCADE = cv2.CascadeClassifier(classifier_path)


def theme_style() -> str:
    # Define the start and end times
    start_time = datetime.strptime("06:30", "%H:%M").time()
    end_time = datetime.strptime("18:30", "%H:%M").time()

    # Get the current time
    now = datetime.now()

    # Check if the current time is within the specified range
    if start_time <= now.time() <= end_time:
        return 'Light'
    else:
        return 'Dark'



def remove_dir(dir_path: Path):
    try:
        # shutil.rmtree(dir_path)
        shutil.rmtree(os.path.join(app_path, dir_path))
    except OSError as e:
        pass



def check_or_make_dir(dir_path: Path) -> None:
    try:
        os.mkdir(os.path.join(app_path, dir_path))
    except Exception as e:
        pass
    return



def simple_check_or_make_dir(dir_path: Path) -> None:
    try:
        os.mkdir(dir_path)
        return True
    except Exception as e:
        pass
    return False



def match_date(date_txt):

    date_pattern = r"\s*([0-3]?[0-9])\W*([0-1]?[0-9])\W*((19|20)[0-9][0-9])\s*"
    match_date = re.search(date_pattern, date_txt, re.IGNORECASE)

    if match_date:

        dd = match_date.group(1)
        if int(dd) > 31 or int(dd) < 1:
            return False

        if len(dd) == 1:
            dd = f"0{dd}"

        mm = match_date.group(2)
        if int(mm) > 12 or int(mm) < 1:
            return False

        if len(mm) == 1:
            mm = f"0{mm}"

        yyyy = match_date.group(3)
        if int(yyyy) > 2100 or int(yyyy) < 1900:
            return False

        return f"{dd}/{mm}/{yyyy}"

    else:
        return False



def match_qty(qty_txt):

    pattern = r"([\d\s]+)"
    match = re.search(pattern, qty_txt, re.IGNORECASE)

    if match:
        qty = re.sub(r"\s+", "", match.group(1))

        if int(qty) < 0 or int(qty) > 1_000_000:
            return False

        return qty

    else:
        return False



def check_image_ext(file_path):

    ext = file_path.split(".")[-1]

    if ext in ["jpg", "JPEG", "jpeg", "png", "svg", "HEIC"]:
        return True
    else:
        return False



def get_all_file_paths(dir_path: Path) -> list[Path]:

    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(os.path.join(app_path, dir_path)):
    # for root, directories, files in os.walk(dir_path):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    return file_paths



def save_face_photo(img_path) -> str:

    if check_image_ext(img_path) == False:
        return "Format d'image non supporté, veuillez utiliser jpg, png ou HEIC."

    else:
        return True



def save_id_photo(img_path) -> str:

    if check_image_ext(img_path) == False:
        return "Format d'image non supporté, veuillez utiliser jpg, png ou HEIC."
    else:
        return True



# TESTS
def test_save_to_external_storage(self):
    # Save a file to external storage
    external_storage_path = "/sdcard/Download/Argus"
    simple_check_or_make_dir(external_storage_path)
    with open(os.path.join(external_storage_path, 'my_file.txt'), 'w') as f:
        f.write('Hello, World!')



def read_qr_from_image(img_path):
    img = cv2.imread(img_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    detector = cv2.QRCodeDetector()

    data, bbox, _ = detector.detectAndDecode(gray)
    if data:
        return data



def save_qr_image(texture, img_path):
    # if texture:
    pixels = texture.pixels
    frame = np.frombuffer(pixels, np.uint8).reshape(texture.height, texture.width, 4)
    cv2.imwrite(img_path, frame)
    return True