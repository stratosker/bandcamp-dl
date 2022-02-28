import sys
import urllib.request
#import requests
import os
import eyed3
import re
import datetime
import argparse
import json
import html

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
	
	sourceCode = sourceCode.decode("utf8")
	sourceCode = sourceCode.replace("&quot;", '"')

	searchObj = re.search( r'data-tralbum="(.*?)="{"', sourceCode, re.M|re.I)

	tracksArr = []
	if searchObj:
		jsonInf = searchObj.group(1)
		reversedjsonInf = jsonInf[::-1] 
		reversedjsonInf= re.sub(r'^.*?"', '', reversedjsonInf)
		jsonInf = reversedjsonInf[::-1]

		albumInfo = json.loads(jsonInf)
		if "trackinfo" in albumInfo:
			for track in albumInfo["trackinfo"]:
				trackInfo = {}
				trackInfo["trackName"] = track["title"]
				trackIsDownloadable = False
				if "file" in track and track["file"] is not None:
					trackInfo["trackLink"] = track["file"]["mp3-128"]
					trackIsDownloadable = True
				trackInfo["trackNum"] = track["track_num"]
				if trackIsDownloadable:
					tracksArr.append(trackInfo)
			foundTrackInfo = True


		if not foundArtistInfo:
			if "artist" in albumInfo:
				artist = albumInfo["artist"]
				foundArtistInfo = True
			else:
				foundArtistInfo = False

		if not foundAlbumInfo:
			if "current" in albumInfo:
				album = albumInfo["current"]["title"]
				foundAlbumInfo = True
			else:
				foundAlbumInfo = False

		if "album_release_date" in albumInfo:
			dateStr = albumInfo["album_release_date"]
			dateStr = dateStr[7: len(dateStr)]
			date_time_obj = datetime.datetime.strptime(dateStr, '%Y %H:%M:%S GMT')
			year = date_time_obj.date().year
			foundYearInfo = True
		else:
			foundYearInfo = False

	tracksCnt = 0
	if tracksArr:
		for track in tracksArr:
			print("Downloading track...")
			tracksCnt+=1
			filename = str(tracksCnt) + ".mp3"

			urllib.request.urlretrieve (track["trackLink"], filename)

			audiofile = eyed3.load(filename)

			if audiofile.tag is None:
				audiofile.tag = eyed3.id3.Tag()
				
				if foundArtistInfo:
					artist = artist.replace('\"','"')
					audiofile.tag.artist = artist
				if foundAlbumInfo:
					album = album.replace('\"','"')
					audiofile.tag.album = album
				if foundTrackInfo:
					track["trackName"] = html.unescape(track["trackName"])
					audiofile.tag.title = track["trackName"]
					if(track["trackNum"]!="null"):
						audiofile.tag.track_num = (track["trackNum"], None)
					else:
						audiofile.tag.track_num = (1, None)
				if foundYearInfo:
					audiofile.tag.original_release_date = year
				audiofile.tag.save(version=(1,None,None))
				audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION,encoding='utf-8')

			if track["trackNum"] < 10:	
				newFilename = "0"+str(track["trackNum"])+" "+track["trackName"]+".mp3"
			else:
				newFilename = str(track["trackNum"])+" "+track["trackName"]+".mp3"

			if (len(newFilename)>=248):
				newFilename = newFilename[:-(len(newFilename)-247)]

			if "/" in newFilename:
					newFilename = newFilename.replace("/", "-")
			if os.name == "nt":
				newFilename = newFilename.replace("<", "")
				newFilename = newFilename.replace(">", "")
				newFilename = newFilename.replace(":", "")
				newFilename = newFilename.replace("\"", "")
				newFilename = newFilename.replace("\\", "")
				newFilename = newFilename.replace("|", "")
				newFilename = newFilename.replace("?", "")
				newFilename = newFilename.replace("*", "")
			os.rename(filename, newFilename)
		
	searchObj = re.search( r'<link rel="image_src" href="(.*)">', sourceCode, re.M|re.I)
	if searchObj:
		cover = searchObj.group(1)
		urllib.request.urlretrieve (cover, "cover.jpg")
	

	print("Download Complete :)")
	

if __name__ == "__main__":
	main(sys.argv[1:])
