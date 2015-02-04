import os #For creating folder
import urllib #For accessing the web
import re #For regex
from urllib.request import urlopen, URLopener
import threading #For downloading multiple files at once
import queue #To create a queue for the threads to pull data from


#Takes in the url of the album, and returns list of lists that contain picture URL endings (eg "ufufuf.jpg") and the extension of the picture (eg "jpg")
def create_pic_list(album_url):
	# Check the URL is actually imgur:
	'''
	match = re.match("(https?)\:\/\/(www\.)?(?:m\.)?imgur\.com/a/([a-zA-Z0-9]+)(#[0-9]+)?", album_url)
	if not match:
		#raise ImgurAlbumException("URL must be a valid Imgur Album")
		print("URL was not valid imgur URL")
	protocol = match.group(1)
		
	album_key = match.group(3)
	'''
	#Get unique album key
	if "gallery" in album_url:
		album_key = album_url.replace("http://imgur.com/gallery/", "")
	elif "/a/" in album_url:
		album_key = album_url.replace("http://imgur.com/a/", "")
	else:
		print("Not valid imgur album URL")
		return False
	#Change current directory to new folder named after 	
	current_dir = os.getcwd()
	dl_path = current_dir + "\\" + album_key
	##This should allow the download location to be changed so that the program can be run off locked flash drive
	#Test to see if directory exists for program already, if not, create one
	if not os.path.exists(dl_path):
		os.makedirs(dl_path)
	#Change working directory to new one
	os.chdir(dl_path)
	

	# Read the no-script version of the page for all the images:
	no_script_url = "http://imgur.com/a/" + album_key + "/noscript"
	#Get html code from album
	try:
		response = urlopen(url=no_script_url)
		response_code = response.getcode()
	except Exception as e:
		response = False
		#response_code = e.code
		print("Error " + str(e))
	
	if not response: # or response.getcode() != 200:
		#raise ImgurAlbumException("Error reading Imgur: Error Code %d" % response_code)
		print("Error reading Imgur")
		return False

	# Read in the images using findall regex
	html = response.read().decode('utf-8')
	#Images now holds a list of all urls of each image
	regexImages = re.findall('<img src="(\/\/i\.imgur\.com\/([a-zA-Z0-9]+\.(jpg|jpeg|png|gif)))(\?[0-9]+)?"', html)
	
	#Remove extra (1st and 4th) columns from finding algorithm (orig. format is like: ('//i.imgur.com/ufufuf.jpg', ufufuf.jpg', 'jpg', '')
	#Creates a list of lists that has only the unique picture key from URL, and then the extension of the picture
	images = []
	for row in regexImages:
		images.append([row[1], row[2]])
	
	return images

#Downloads picture into current directory, naming it the "name" passed in
#Takes the ending key of the picture to be downloaded (eg s1K6Ny.jpg) as well as the name that the file should be called
def download_pic(pic_key, name):
	#Format of url: http://i.imgur.com/KTqYYKVh.jpg
	
	#Create full URL for download of picture
	url = "http://i.imgur.com/" + pic_key
	#Check if there is a picture with this name already
	#Either rename or skip
	if os.path.isfile(name):
		return True
		#return False
		'''
		#Add "_1" to the end of the picture name if name is taken
		name = "1_" + name
		'''
	
	#Create object to open url
	picture = URLopener()	
	#Try to download picture and save as name
	try:
		picture.retrieve(url, name)
	except: #Error in downloading picture
		return False
	#Return True if process completes, meaning that picture downloaded
	return True
	

# The worker thread pulls an item from the queue and downloads it
def worker():
	while True:
		item = pics_queue.get()
		#Create name for picture using position in album and picture name
		pic_name = str(item[1]) + "_" + item[0]
		#If the download fails, add to queue of failed downloads
		if not download_pic(item[0], pic_name):
			failed_dl.put(item)
			#Use lock to serialize output
			with lock:
				print("FAILED:", pic_name, "in", threading.current_thread().name)
		#Use lock to serialize output
		with lock:
			print("Downloaded", pic_name, "in", threading.current_thread().name)
		pics_queue.task_done()
	

if __name__ == '__main__':
	#Test http://imgur.com/a/poltD
	url_in = input("Input url: ")
	pics = create_pic_list(url_in)
	#If the list could be created:
	if pics:
		#Print stats about info
		print(len(pics), "images in gallery")
		#Get number of each extension type
		extension_count = {}
		for i in pics:
			#If key is already in dict
			if i[1] in extension_count:
				#Increment count of extension
				extension_count[i[1]] = extension_count[i[1]] + 1
			#If first occurrence of extension, create entry
			else:
				extension_count[i[1]] = 1
		
		#Print dict of extensions by iterating through
		for key in extension_count:
			print(extension_count[key], key, "images")
		
		#Create queue of data so that threads can all access data
		pics_queue = queue.Queue()
		for i,image in enumerate(pics):
			pics_queue.put([image[0], i+1])
		
		#Create empty queue to store failed download keys
		failed_dl = queue.Queue()
		
		# lock to serialize console output
		lock = threading.Lock()

		#Number of threads to start to process data
		num_of_threads = 1
		print("Beginning download of album with", num_of_threads, "threads")
		
		#Create number of threads specified
		for i in range(num_of_threads):
			 t = threading.Thread(target=worker)
			 t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
			 t.start()
		#Wait until all tasks have finished, lock until done
		pics_queue.join()
		
		'''
		print(pics)
		print(len(pics))
		print(pics[0][0])
		#Test download
		print("Download complete:", download_pic(pics[0][0], pics[0][0]))
		'''	