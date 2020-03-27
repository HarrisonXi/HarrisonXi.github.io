# -*- coding:utf-8 -*- 
import re
import sys,os

postNamePattern = re.compile(r'(\d{4})-(\d{2})-\d{2}-(.+)\.md')
categoryPattern = re.compile(r'categories: \[?([^,\n]+)')

def makeReadme(DIR):
	# 遍历所有有效的post
	matchedPosts = []
	for path in os.listdir(DIR):
		fullPath = os.path.join(DIR, path)
		if os.path.isfile(fullPath):
			if path.lower().endswith('.md'):
				match = postNamePattern.match(path)
				if match:
					print('Adding post: {}'.format(match.group(3)))
					matchedPosts.append(path)
	# 创建文件头内容
	readmeContent = '# [苹果梨的博客](https://blog.harrisonxi.com)\n'
	# 按年月分类post并创建列表
	matchedPosts = sorted(matchedPosts, reverse = True)
	year = ''
	month = ''
	for post in matchedPosts:
		match = postNamePattern.match(post)
		if match:
			if year != match.group(1) or month != match.group(2):
				year = match.group(1)
				month = match.group(2)
				readmeContent = readmeContent + '\n### {}-{}\n'.format(year, month)
			file = open(os.path.join(DIR, post), 'r')
			content = file.read()
			file.close()
			categoryMatch = categoryPattern.search(content)
			categoryName = '未分类'
			if categoryMatch:
				categoryName = categoryMatch.group(1)
			readmeContent = readmeContent + '\n`{}` [{}](https://blog.harrisonxi.com/{}/{}/{}.html)\n'.format(categoryName, match.group(3), year, month, match.group(3).replace(' ', '%20'))
	# 写入文件内容
	file = open('source/README.md', 'w')
	file.write(readmeContent)
	file.close()

makeReadme(os.path.join(os.getcwd(), 'source/_posts'))
print('README is generated.')
