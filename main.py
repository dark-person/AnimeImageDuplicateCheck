import logging
import os
from pathlib import Path

import imagehash
from PIL import Image

# Const for default image directory
image_input_directory = "input"
image_output_directory = "best-output"
image_duplicate_directory = "duplicate-out"

# Logger
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('activity.log', encoding='utf-8')
fh.setLevel(logging.DEBUG)

formatter2 = logging.Formatter("%(asctime)s - %(levelname)-8s : %(message)s")
fh.setFormatter(formatter2)

logger.addHandler(fh)
logger.propagate = False


def get_input_filelist():
    suffix_list = ["jpg", "jpeg", "png"]

    image_list = []
    for filename in os.listdir(image_input_directory):
        if filename.split('.')[-1].lower() in suffix_list:
            image_list.append('input/' + filename)
    image_list.sort()

    logger.debug("Image List : %s", str(image_list))
    print("Got File List in the input. Start processing...")

    return image_list


def get_image_hash(filepath: str):
    phash = imagehash.phash(Image.open(filepath), hash_size=19)
    logger.debug('Filename = %s, phash = %s', filepath, phash)
    return str(phash)


def get_duplicate_dict(filenames: list):
    hashmap = dict()
    print("Starting analyze image..")

    for idx, filename in enumerate(filenames):
        if idx % 10 == 0 and idx != 0:
            print("Analyzed Image ", idx, "/", len(filenames))
        hash_value = get_image_hash(filename)
        # print(hash_value, " ", hashmap)
        # print((hash_value not in hashmap))
        if hash_value not in hashmap:
            hashmap[hash_value] = [filename]
        else:
            temp = hashmap[hash_value]
            temp.append(filename)
            hashmap[hash_value] = temp

    print("Analyze image completed. Start Comparing..")
    return hashmap


def seperate_image(image_list: list):
    best_image = image_list[0]

    for i in range(1, len(image_list)):
        width1, height1 = Image.open(best_image).size
        width2, height2 = Image.open(image_list[i]).size
        logger.debug("Current Best Image: %d x %d", width1, height1)
        logger.debug("Image[%d]         : %d x %d", i, width2, height2)
        if (width2 > width1 and height2 >= height1) or (width2 >= width1 and height2 > height1):
            best_image = image_list[i]
        elif width2 == width1 and height2 == height1:
            filesize1 = os.path.getsize(best_image)
            filesize2 = os.path.getsize(image_list[i])
            logger.debug("Image Width Height Equal. Start compare size:")
            logger.debug("Best: %s, Current:%s", str(filesize1), str(filesize2))
            if filesize2 > filesize1:
                best_image = image_list[i]

    image_list.remove(best_image)
    return best_image, image_list


def move_duplicate_file(duplicated_list: list):
    Path(image_duplicate_directory).mkdir(exist_ok=True)
    for filepath in duplicated_list:
        file = Path(filepath)
        file.rename(image_duplicate_directory + "/" + file.name)


def move_best_file(best_list: list):
    Path(image_output_directory).mkdir(exist_ok=True)
    for filepath in best_list:
        file = Path(filepath)
        file.rename(image_output_directory + "/" + file.name)


filelist = get_input_filelist()
hash_dict = get_duplicate_dict(filelist)

final_image_list = []
print("Detect Uniqnue image: ", len(hash_dict), ". Start Comparing..")
for index, item in enumerate(hash_dict.values()):
    if index % 10 == 0 and index != 0:
        print("Compared Image ", index, "/", len(hash_dict))
    if len(item) > 1:
        best, duplicated = seperate_image(item)
        final_image_list.append(best)
        logger.debug("Best: %s, Duplicate: %s", best, str(duplicated))
        print("Compared Image : Image: ", best, " has duplicate file of ", len(duplicated), " : ", duplicated)
        move_duplicate_file(duplicated)
    else:
        final_image_list.append(item[0])
# print("Here is final images : ", final_image_list)
move_best_file(final_image_list)
print("The whole process is completed.")
