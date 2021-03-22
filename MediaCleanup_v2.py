import os
import sys
import hashlib ##used to get file hash value
import shutil ##used for file copy
from dateutil.parser import parse
import exifread
import datetime

class PhotoFile:
    """Class to represent an image file (jpg, png, etc...)"""
    def __init__(self, file_path, filename):
        self.file_path = file_path
        self.filename = filename
        self.new_path = file_path
        self.file_extension = self.filename.split('.')[-1]
    
    def __exif_image_datetime(self):
        """Private Method that opens the image file, reads the exif tags, and returns the Image DateTime tag as a datetime object."""
        try:
            self.full_path = os.path.join(self.file_path, self.filename)
            f = open(self.full_path, 'rb')
            tags = exifread.process_file(f)
            
            exif_datetime = tags.get('Image DateTime')
        except:
            exif_datetime = None
            print(f"Unable to extract exif data for {self.filename}")
    
        if exif_datetime:
            exif_datetime = str(tags['Image DateTime'])[0:10].replace(":","-") #Strip to only the YYYY:MM:DD value and replace : with - for easier parsing
        
        ##If we couldn't get the exif tag or it is a bad date, get the create timestamp
        if exif_datetime is None or exif_datetime == '0000-00-00':
            try:
                exif_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(self.file_path, self.filename))).strftime("%Y-%m-%d")
            except:
                print("Unable to get the file create timestamp")
                exif_datetime = 'unknown'
        
        if exif_datetime is None:
            print(f"Issue with {self.filename}")

        return exif_datetime

    def determine_new_directory(self, new_root_path):
        photo_datetime = self.__exif_image_datetime()
        print(f"Exif datetime tag = {photo_datetime}")
        if photo_datetime != 'unknown' and photo_datetime != '0000-00-00':
            photo_datetime = parse(photo_datetime)
            year = photo_datetime.strftime("%Y")
            month_name = photo_datetime.strftime("%B")
            path = os.path.join(new_root_path,'Photos',year,month_name)
        else:
            path = os.path.join(new_root_path,'Photos',photo_datetime)
        
        return(path)

class VideoFile:
    def __init__(self, file_path, filename):
        self.file_path = file_path
        self.filename = filename
        self.new_path = file_path
        self.file_extension = self.filename.split('.')[-1]

    def determine_new_directory(self,new_root_path):
        video_datetime = self.__get_create_datetime()
        print(f"Create datetime = {video_datetime}")
        if video_datetime != 'unknown':
            video_datetime = parse(video_datetime)
            year = video_datetime.strftime("%Y")
            month_name = video_datetime.strftime("%B")
            path = os.path.join(new_root_path,'Video',year,month_name)
        else:
            path = os.path.join(new_root_path,'Video',video_datetime)
        
        return(path)

    def __get_create_datetime(self):
        """Private Method that gets the file create time for the movie file."""
        try:
            create_date = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(self.file_path, self.filename))).strftime("%Y-%m-%d")
        except:
            print(f"Unable to get create timestamp for {self.filename}")
            create_date = 'unknown'

        return create_date

class NonMediaFile:
    def __init__(self, file_path, filename):
        self.file_path = file_path
        self.filename = filename
        self.new_path = file_path
        self.file_extension = self.filename.split('.')[-1]   
    
    def determine_new_directory(self,new_root_path):
        return(os.path.join(new_root_path,'Non Media Files'))    

class MediaCleanup:
    def __init__(self):
        self.source_root_path = os.getcwd() ##default to current dir
        self.target_root_path = os.path.join(self.source_root_path, 'CleanedUp')

    def __create_path_if_needed(self,file_path):
        if not os.path.isdir(file_path):
            os.makedirs(file_path)

    def cleanup(self):
        photo_dictionary = {}
        video_dictionary = {}
        other_dictionary = {}
        image_cnt = 0 
        video_cnt = 0
        other_cnt = 0

        walk_dir = self.source_root_path

        for root, subdirs, files in os.walk(walk_dir):
            print('--\nroot = ' + root)

            for filename in files:
                file_path = os.path.join(root, filename)
                print(f"\t-- file {filename} (full path: {file_path})")

                if filename.lower().split('.')[-1] in ('jpg', 'jpeg', 'bmp'):
                    image_cnt += 1
                    print(f"\t Processing image file {filename}")
                    ##Read the file in binary mode and generate the sha256 hash
                    file_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()
                    
                    photo_obj = PhotoFile(root, filename)
                    photo_obj.new_path = photo_obj.determine_new_directory(self.target_root_path)

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
                elif filename.lower().split('.')[-1] in ('avi', 'mp4', 'mpg', 'wmv', 'mov'):
                    video_cnt += 1
                    print(f"\tProcessing video file {filename}")
                    file_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()

                    video_obj = VideoFile(root, filename)
                    video_obj.new_path = video_obj.determine_new_directory(self.target_root_path)

                    if video_dictionary.get(file_hash):
                        ##Retrieve the list and append
                        print(f"\t\t Duplicate Video")
                        current_video = video_dictionary[file_hash]

                        ##If this filename is shorter than the what is in the dictionary, replace it
                        if len(video_obj.filename) < len(current_video.filename):
                            video_dictionary[file_hash] = video_obj
                    else:
                        ##Insert the new hash into the dictionary as a one item list
                        print(f"\t\t Unique Video")
                        video_dictionary[file_hash] = video_obj
                else: ##All other files     
                    print(f"\tProcessing other file type {filename}")
                    other_cnt += 1
                    file_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()

                    other_file_obj = NonMediaFile(root, filename)
                    other_file_obj.new_path = other_file_obj.determine_new_directory(self.target_root_path)

                    if other_dictionary.get(file_hash):
                        ##Retrieve the list and append
                        print(f"\t\t Duplicate File")
                        current_file = other_dictionary[file_hash]

                        ##If this filename is shorter than the what is in the dictionary, replace it
                        if len(other_file_obj.filename) < len(current_file.filename):
                            other_dictionary[file_hash] = other_file_obj
                    else:
                        ##Insert the new hash into the dictionary as a one item list
                        print(f"\t\t Unique Video")
                        other_dictionary[file_hash] = other_file_obj

        print(f"There are {image_cnt} total images and {len(photo_dictionary)} unique images. Copying photos now...")

        for photo in photo_dictionary.values():
            print(f"Copying file from {photo.file_path} to {photo.new_path}")
            self.__create_path_if_needed(photo.new_path)
            shutil.copy(os.path.join(photo.file_path, photo.filename), os.path.join(photo.new_path, photo.filename))

        print(f"There are {video_cnt} total videos and {len(video_dictionary)} unique videos. Copying videos now...")

        for video in video_dictionary.values():
            print(f"Copying file from {video.file_path} to {video.new_path}")
            self.__create_path_if_needed(video.new_path)
            shutil.copy(os.path.join(video.file_path, video.filename), os.path.join(video.new_path, video.filename))

        print(f"There are {other_cnt} total files and {len(other_dictionary)} unique non-media files. Copying files now...")

        for other_file in other_dictionary.values():
            print(f"Copying file from {other_file.file_path} to {other_file.new_path}")
            self.__create_path_if_needed(other_file.new_path)
            shutil.copy(os.path.join(other_file.file_path, other_file.filename), os.path.join(other_file.new_path, other_file.filename))


#walk_dir = 'D:\\Parents Pictures\\'
#walk_dir = 'C:\\Users\\Derek\\Desktop\\duplicate_pictures\\'
#new_root_dir = 'C:\\Users\\Derek\\Desktop\\Cleaned Up Pictures\\'
#new_root_dir = 'D:\\Cleaned Up Pictures\\'

if __name__ == '__main__':
    mc = MediaCleanup()
    #mc.source_root_path = 'C:\\Users\\Derek\\Desktop\\duplicate_pictures\\'
    #mc.target_root_path = 'C:\\Users\\Derek\\Desktop\\Cleaned Up Pictures\\'
    mc.source_root_path = 'C:\\Parents Pictures\\'
    mc.target_root_path = 'D:\\Cleaned Up Pictures\\'
    mc.cleanup()