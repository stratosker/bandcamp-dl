import sys
import urllib.request
#import requests
import os
import eyed3
import re

#Usage
#python bandcamp-dl.py [album/track link]

def main(argv): 
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

	foundTrackInfo = True
	foundArtistInfo = False
	foundAlbumInfo = False
	searchObj = re.search( r'album_title(.*): "(.*)"', sourceCode, re.M|re.I)
	if searchObj:
		album = searchObj.group(2)
		album = album.replace('\"','"')
		#print(album)
		foundAlbumInfo = True
	else:
		#print("no album")
		foundAlbumInfo = False
	searchObj = re.search( r'artist: "(.*)"', sourceCode, re.M|re.I)
	if searchObj:
		artist = searchObj.group(1)
		artist = artist.replace('\"','"')
		#print(artist)
		foundArtistInfo = True
	else:
		#print("no artist")
		foundArtistInfo = False

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
					track = track.replace("&quot;", '"')
					track = track.replace("&lt;", '<')
					track = track.replace("&gt;", '>')
					track = track.replace("&amp;amp;", "&")
					track = track.replace("&amp;", '&')
					foundTrackInfo = True
				else:
					foundTrackInfo = False
				if(not foundTrackInfo):
					#print("Finding track info...")
					#searchObj = re.search(r'{"play_count"(.*)"title":"(.*)"(.*)"track_num":(.*),(.*)"mp3-128":"https://'+re.escape(downUrl)+r'"', sourceCode, re.M|re.I) 
					searchObj = re.search(r'trackinfo:(.*)"title":"(.*)"(.*)"track_num":(.*),(.*)"mp3-128":"https://'+re.escape(downUrl)+r'"', sourceCode, re.M|re.I)
					if searchObj:
						track  = searchObj.group(2).split('","')[0]
						trackNum =  searchObj.group(4).split(',"')[0]
						#print(trackNum+" "+ track)
						foundTrackInfo = True
					else:
						searchObj = re.search(r'trackinfo:(.*)"title":"(.*)"(.*)"track_num":(.*),', sourceCode, re.M|re.I)
						if searchObj:
							track  = searchObj.group(2).split('","')[0]
							trackNum =  searchObj.group(4).split(',"')[0]
							#print(trackNum+" "+ track)
							foundTrackInfo = True
						else:
							foundTrackInfo = False
				if foundArtistInfo:
					audiofile.tag.artist = artist
				if foundAlbumInfo:
					audiofile.tag.album = album
				if foundTrackInfo:
					audiofile.tag.title = track
					if(trackNum!="null"):
						audiofile.tag.track_num = (trackNum, None)
					else:
						audiofile.tag.track_num = (1, None)
				audiofile.tag.save(version=(1,None,None))
				audiofile.tag.save()
				#else:
					#continue
			
			#print("Renamening file...")	
			if(foundTrackInfo):
				name = audiofile.tag.title
				if (len(name)>=248):
					name = name[:-(len(name)-247)]
				if "/" in name:
					name = name.replace("/", "-")
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
