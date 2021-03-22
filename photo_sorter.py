#!/usr/bin/env python3

import os
import sys
import hashlib ##used to get file hash value
from PhotoFileProperties import PhotoFileProperties
import shutil ##used for file copy
from dateutil.parser import parse

walk_dir = 'D:\\Parents Pictures\\'
#walk_dir = 'C:\\Users\\Derek\\Desktop\\duplicate_pictures\\'
#new_root_dir = 'C:\\Users\\Derek\\Desktop\\Cleaned Up Pictures\\'
new_root_dir = 'D:\\Cleaned Up Pictures\\'

print('walk_dir = ' + walk_dir)

##Dictionary to store the list of pictures
### key is the file hash
### value is a list of photo objects
photo_dictionary = {}
image_cnt = 0 

for root, subdirs, files in os.walk(walk_dir):
    print('--\nroot = ' + root)

    for filename in files:
        file_path = os.path.join(root, filename)
        print(f"\t-- file {filename} (full path: {file_path})")

        if filename.lower().split('.')[-1] == 'jpg':
            image_cnt += 1
            print(f"\t Processing image file {filename}")
            ##Read the file in binary mode and generate the sha256 hash
            file_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()
            
            photo_obj = PhotoFileProperties(root, filename)

            if photo_dictionary.get(file_hash):
                ##Retrieve the list and append
                print(f"\t\t Duplicate Photo")
                current_photo = photo_dictionary[file_hash]

                ##If this filename is shorter than the what is in the dictionary, replace it
                if len(photo_obj.filename) < len(current_photo.filename):
                    photo_dictionary[file_hash] = photo_obj
            else:
                ##Insert the new hash into the dictionary as a one item list
                print(f"\t\t Unique Photo")
                photo_dictionary[file_hash] = photo_obj
        else:
            print(f"File {filename} is not an image.")

print(f"There are {image_cnt} total images and {len(photo_dictionary)} unique images.")

def determine_new_directory(root_path,photo):
    photo_datetime = photo.exif_image_datetime()
    print(f"Exif datetime tag = {photo_datetime}")
    year = photo_datetime.strftime("%Y")
    month_name = photo_datetime.strftime("%B")

    return(os.path.join(root_path,year,month_name))

def create_path_if_needed(file_path):
    if not os.path.isdir(file_path):
        os.makedirs(file_path)

for photo in photo_dictionary.values():
    new_dir = determine_new_directory(new_root_dir, photo)
    print(f"Copying file from {photo.file_path} to {new_dir}")
    create_path_if_needed(new_dir)
    shutil.copy(os.path.join(photo.file_path, photo.filename), os.path.join(new_dir, photo.filename))
    