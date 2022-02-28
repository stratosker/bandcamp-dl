import sys
import urllib.request
#import requests
import os
import eyed3
import re
import datetime
import argparse
import json

#Usage
#python bandcamp-dl.py album/track link [--artist ARTIST] [--album ALBUM]

def main(argv): 
	foundTrackInfo = False
	foundArtistInfo = False
	foundAlbumInfo = False

	parser = argparse.ArgumentParser(description='Album link and metadata')
	parser.add_argument('link')
	parser.add_argument('--artist', dest='artist', type=str, help='Artist')
	parser.add_argument('--album', dest='album', type=str, help='Album')

	args = parser.parse_args()
	if args.artist:
		artist = args.artist
		foundArtistInfo = True

	if args.album:
		album = args.album
		foundAlbumInfo = True
	

	folderName = input("Enter the folder name where the files will be saved(enter . for current directory): ")
	if(folderName!="."):
		if (os.path.isdir(folderName) == False):
			os.mkdir(folderName)
		os.chdir(folderName)
	with urllib.request.urlopen(sys.argv[1]) as response:
		sourceCode = response.read()
	print(("Downloading "+sys.argv[1])) 
	fileName = 0
	it = 0
	
	sourceCode = sourceCode.decode("utf8")
	sourceCode = sourceCode.replace("&quot;", '"')

	searchObj = re.search( r'<script type="application/ld\+json">\n(.*)', sourceCode, re.M|re.I)

	if searchObj:
		jsonInf = searchObj.group(1)
		albumInfo = json.loads(jsonInf)

		if not foundArtistInfo :
			if "byArtist" in albumInfo and "name" in albumInfo["byArtist"]:
				artist = albumInfo["byArtist"]["name"]
				foundArtistInfo = True
			else:
				foundArtistInfo = False

		if not foundAlbumInfo:
			if "name" in albumInfo:
				album = albumInfo["name"]
				foundAlbumInfo = True
			else:
				foundAlbumInfo = False

		if "datePublished" in albumInfo:
			dateStr = albumInfo["datePublished"]
			dateStr = dateStr[7: len(dateStr)]
			date_time_obj = datetime.datetime.strptime(dateStr, '%Y %H:%M:%S GMT')
			year = date_time_obj.date().year
			foundYearInfo = True
		else:
			foundYearInfo = False


	for x in sourceCode:
		if((x=="t" or x=="p") and sourceCode[it+1]=="4" and sourceCode[it+2]=="." and sourceCode[it+3]=="b" and sourceCode[it+4]=="c" and sourceCode[it+5]=="b"):
			it2 = it
			downUrl = ""
			fileName += 1
			while sourceCode[it2]!='"':
				downUrl+=str(sourceCode[it2])
				it2 = it2+1
			#r = requests.get("http://"+downUrl, allow_redirects=False)
			#req = urllib.request.Request(downUrl, datagen, headers)
			#print (r.headers['Location'])
			print("downloading track...")
			#urllib.request.urlretrieve(r.headers['Location'], str(fileName)+".mp3")
			urllib.request.urlretrieve ("http://"+downUrl, str(fileName)+".mp3")
			filename = str(fileName)+".mp3"
			trackNum  = filename.split('.mp3')[0]
			audiofile = eyed3.load(filename)
			if audiofile.tag is None:
				audiofile.tag = eyed3.id3.Tag()
				
				searchObj = re.search(r'\n'+re.escape(trackNum) +r'\. (.*)', sourceCode, re.M|re.I)
				if searchObj:
					track = searchObj.group(1)
					track = track.replace("&#39;", "'")
					track = track.replace("&amp;#39;", "'")
					track = track.replace('&amp;quot;', '"')
					track = track.replace("&quot;", '"')
					track = track.replace("&lt;", '<')
					track = track.replace("&gt;", '>')
					track = track.replace("&amp;amp;", "&")
					track = track.replace("&amp;", '&')
					foundTrackInfo = True
				else:
					foundTrackInfo = False
				
				if foundArtistInfo:
					artist = artist.replace('\"','"')
					audiofile.tag.artist = artist
				if foundAlbumInfo:
					album = album.replace('\"','"')
					audiofile.tag.album = album
				if foundTrackInfo:
					audiofile.tag.title = track
					if(trackNum!="null"):
						audiofile.tag.track_num = (trackNum, None)
					else:
						audiofile.tag.track_num = (1, None)
				if foundYearInfo:
					audiofile.tag.original_release_date = year
				audiofile.tag.save(version=(1,None,None))
				audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION,encoding='utf-8')
				#else:
					#continue
			
			#print("Renamening file...")	
			if(foundTrackInfo):
				name = audiofile.tag.title
				if (len(name)>=248):
					name = name[:-(len(name)-247)]
				if "/" in name:
					name = name.replace("/", "-")
				if os.name == "nt":
					name = name.replace("<", "")
					name = name.replace(">", "")
					name = name.replace(":", "")
					name = name.replace("\"", "")
					name = name.replace("\\", "")
					name = name.replace("|", "")
					name = name.replace("?", "")
					name = name.replace("*", "")
				if(len(str(audiofile.tag.track_num[0]))==1):	
					os.rename(filename, "0"+str(audiofile.tag.track_num[0])+" "+name+".mp3")
				else:
					os.rename(filename, str(audiofile.tag.track_num[0])+" "+name+".mp3")
		it=it+1

	searchObj = re.search( r'<link rel="image_src" href="(.*)">', sourceCode, re.M|re.I)
	if searchObj:
		cover = searchObj.group(1)
		urllib.request.urlretrieve (cover, "cover.jpg")
	

	print("Download Complete :)")
	

if __name__ == "__main__":
	main(sys.argv[1:])
