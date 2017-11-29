# -*- coding:utf-8 -*- 
import re
import sys,os

def tab2space(DIR):
	for path in os.listdir(DIR):
		fullPath = os.path.join(DIR, path)
		if os.path.isfile(fullPath):
			if path.lower().endswith('.md'):
				print('Processing: %s' % (path))
				mdFile = open(fullPath, 'r+')
				content = mdFile.read()
				content = re.sub("\t", "    ", content)
				mdFile.seek(0)
				mdFile.write(content)
				mdFile.truncate()
				mdFile.close()

tab2space(os.path.join(os.getcwd(), '_posts'))
print('Tab to space convertion is done.')
