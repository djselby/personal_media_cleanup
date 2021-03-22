#!/usr/bin/env python3

import os
import sys
import exifread
import hashlib

walk_dir = 'D:\\Parents Pictures\\'

print('walk_dir = ' + walk_dir)

# If your current working directory may change during script execution, it's recommended to
# immediately convert program arguments to an absolute path. Then the variable root below will
# be an absolute path as well. Example:
# walk_dir = os.path.abspath(walk_dir)
print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

for root, subdirs, files in os.walk(walk_dir):
    print('--\nroot = ' + root)

    for subdir in subdirs:
        print('\t- subdirectory ' + subdir)

    for filename in files:
        file_path = os.path.join(root, filename)
        print('\t- file %s (full path: %s)' % (filename, file_path))

        if '.jpg' in filename.lower():
            f = open(file_path, 'rb')
            # Return Exif tags
            tags = exifread.process_file(f)
            file_hash = hashlib.sha256(f.read()).hexdigest()
            print(f"File hash = {file_hash}")
            print(f"------- Reading tags for {filename}")
            datetime = tags['Image DateTime']
            
            #for tag in tags.keys():
            #    if tag in ('Image DateTime'):
            #        print( "Key: %s, value %s" % (tag, tags[tag]) )
        else:
            print(f"File {filename} is not an image.")


##Exif Image Datetime
##File hash
##Current File Path
##New File Path
##Duplicate
