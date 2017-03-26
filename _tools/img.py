# -*- coding:utf-8 -*- 
import re
import sys,os

def convertImg(DIR):
	for path in os.listdir(DIR):
		fullPath = os.path.join(DIR, path)
		if os.path.isdir(fullPath):
			convertImg(fullPath)
		elif os.path.isfile(fullPath):
			if path.lower().endswith('.html'):
				print('Converting: %s' % (path))
				htmlFile = open(fullPath, 'r+')
				content = htmlFile.read()
				content = re.sub("src='\.\./\d{4}/\d{2}/(\d{2}-[A-Z].png)'",
					   		     "src='\g<1>'",
					    		 content)
				htmlFile.seek(0)
				htmlFile.write(content)
				htmlFile.truncate()
				htmlFile.close()

convertImg(os.getcwd())
print('Img convertion is done.')
