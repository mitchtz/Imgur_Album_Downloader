# Imgur_Album_Downloader
Downloads all the images in an Imgur album or gallery
This program circumvents using Imgur's built in album or gallery export tool, as it can take quite a while to zip and send you a link to the file. This program will create a new directory in the running directory and download each picture, naming it with the number in the series it is, as well as with the picture id. Will skip downloading if the filename is already taken, so duplicates are ignored if program is run twice. Threading is also utilized to speed up downloading, and the number of threads is variable.
