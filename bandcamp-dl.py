import sys
import urllib
import urllib2
#import requests
import os
import eyed3

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
	for x in sourceCode:
		if((x=="t" or x=="p") and sourceCode[it+1]=="4" and sourceCode[it+2]=="." and sourceCode[it+3]=="b" and sourceCode[it+4]=="c" and sourceCode[it+5]=="b"):
			it2 = it
			downUrl = ""
			fileName += 1
			while sourceCode[it2]!='"':
				downUrl+=str(sourceCode[it2])
				it2 = it2+1
			#r = requests.get("http://"+downUrl, allow_redirects=False)
			#req = urllib2.Request(downUrl, datagen, headers)
			#print (r.headers['Location'])
			print("downloading track...")
			#urllib.urlretrieve (r.headers['Location'], str(fileName)+".mp3")
			urllib.request.urlretrieve ("http://"+downUrl, str(fileName)+".mp3")
		it=it+1
	
	for filename in os.listdir("."):
		if filename.endswith(".mp3"):
			audiofile = eyed3.load(filename)
			if audiofile.tag is None:
				print("not able to extract track info")
				continue
			name = audiofile.tag.title
			if (len(name)>=248):
				name = name[:-(len(name)-247)]
			if "/" in name:
				name = name.replace("/", "-")
			if(len(str(audiofile.tag.track_num[0]))==1):	
				os.rename(filename, "0"+str(audiofile.tag.track_num[0])+" "+name+".mp3")
			else:
				os.rename(filename, str(audiofile.tag.track_num[0])+" "+name+".mp3")
	
	print("Downloading Complete :)")
	

if __name__ == "__main__":
	main(sys.argv[1:])
