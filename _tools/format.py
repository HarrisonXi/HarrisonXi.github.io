# -*- coding:utf-8 -*- 
import re
import sys,os
from subprocess import call

def formatHtml(DIR):
	for path in os.listdir(DIR):
		fullPath = os.path.join(DIR, path)
		if os.path.isdir(fullPath):
			formatHtml(fullPath)
		elif os.path.isfile(fullPath):
			if path.lower().endswith('.html'):
				print('Formatting: %s' % (path))
				call(['tidy', '-m', '-w', '-i', '-q', fullPath])

formatHtml(os.getcwd())
print('HTML formatting is done.')
