# -*- coding:utf-8 -*- 
import re
import sys,os

def tabToSpace(DIR):
	for path in os.listdir(DIR):
		fullPath = os.path.join(DIR, path)
		if os.path.isfile(fullPath):
			if path.lower().endswith('.md'):
				print('Processing: %s' % (path))
				mdFile = open(fullPath, 'r+')
				content = mdFile.read()
				newContent = re.sub("\t", "    ", content)
				if newContent != content:
					mdFile.seek(0)
					mdFile.write(content)
					mdFile.truncate()
				mdFile.close()

tabToSpace(os.path.join(os.getcwd(), 'source/_posts'))
print('Tab to space convertion is done.')
