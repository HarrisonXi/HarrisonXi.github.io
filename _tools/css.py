# -*- coding:utf-8 -*- 
import re
import sys,os

def convertCss(DIR):
	for path in os.listdir(DIR):
		fullPath = os.path.join(DIR, path)
		if os.path.isdir(fullPath):
			convertCss(fullPath)
		elif os.path.isfile(fullPath):
			if path.lower().endswith('.html'):
				print('Converting: %s' % (path))
				htmlFile = open(fullPath, 'r+')
				content = htmlFile.read()
				content = re.sub("<style type='text/css'>[^<]+</style>",
					   		     "<link href='/css/github.css' rel='stylesheet' type='text/css'>" +
					   		     "<link href='/css/myblog.css' rel='stylesheet' type='text/css'>",
					    		 content)
				htmlFile.seek(0)
				htmlFile.write(content)
				htmlFile.truncate()
				htmlFile.close()

convertCss(os.getcwd())
print('Css convertion is done.')
