# -*- coding:utf-8 -*- 
import re
import sys,os

script = '''/title>
  <script async src="https://www.googletagmanager.com/gtag/js?id=UA-110376743-1"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'UA-110376743-1');
  </script>
  <link'''

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
				content = re.sub("/title>\s*<link", script, content)
				htmlFile.seek(0)
				htmlFile.write(content)
				htmlFile.truncate()
				htmlFile.close()

convertCss(os.getcwd())
print('Analytics script is added.')
