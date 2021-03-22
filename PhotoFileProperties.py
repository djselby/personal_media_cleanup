import exifread
import os

from datetime import datetime

class PhotoFileProperties:
    """Class to represent an image file (jpg, png, etc...)"""
    def __init__(self,file_path, filename):
        self.file_path_root = file_path
        self.filename = filename
        self.file_path = file_path
        ##
        self.new_path = ''
        self.keep_photo = False
        
    def exif_image_datetime(self):
        """Method that opens the image file, reads the exif tags, and returns the Image DateTime tag as a datetime object."""
        self.full_path = os.path.join(self.file_path, self.filename)
        f = open(self.full_path, 'rb')
        tags = exifread.process_file(f)
        
        exif_datetime = tags.get('Image DateTime')

        if exif_datetime:
            exif_datetime = str(tags['Image DateTime'])[0:10].replace(":","-") #Strip to only the YYYYMMDD value and replace : with - for easier parsing
        else:
            exif_datetime = 'unknown'
        return exif_datetime
