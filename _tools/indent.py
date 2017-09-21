# -*- coding:utf-8 -*- 
import re
import sys,os

def convertIndent(DIR):
	for path in os.listdir(DIR):
		fullPath = os.path.join(DIR, path)
		if os.path.isdir(fullPath):
			convertIndent(fullPath)
		elif os.path.isfile(fullPath):
			if path.lower().endswith('.html'):
				print('Converting: %s' % (path))
				htmlFile = open(fullPath, 'r+')
				content = htmlFile.read()
				content = re.sub('<span class="md-toc-item md-toc-h4"[^>]*><a[^>]+>[^<]+</a></span>',
								 '',
								 content)
				content = re.sub("md-toc-item md-toc-h3", "md-toc-h2 md-toc-item", content)
				content = re.sub("md-toc-item md-toc-h5", "md-toc-h3 md-toc-item", content)
				htmlFile.seek(0)
				htmlFile.write(content)
				htmlFile.truncate()
				htmlFile.close()

convertIndent(os.getcwd())
print('Indent convertion is done.')
