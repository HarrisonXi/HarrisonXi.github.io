# -*- coding:utf-8 -*- 
import re
import sys,os

postNamePattern = re.compile(r'(\d{4})-(\d{2})-\d{2}-(.+)\.md')

def makeIndex(DIR):
	# 遍历所有有效的post
	matchedPosts = []
	for path in os.listdir(DIR):
		fullPath = os.path.join(DIR, path)
		if os.path.isfile(fullPath):
			if path.lower().endswith('.md'):
				match = postNamePattern.match(path)
				if match:
					print('Adding post: %s' % (match.group(3)))
					matchedPosts.append(path)
	# 创建文件头内容
	readmeContent = '# [苹果梨的博客](http://blog.harrisonxi.com)\n'
	indexContent = '---\ntitle: 苹果梨的博客 - 首页\n---\n\n# 苹果梨的博客\n'
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
				readmeContent = readmeContent + '\n### %s-%s\n' % (year, month)
				indexContent = indexContent + '\n### %s-%s\n' % (year, month)
			readmeContent = readmeContent + '\n[%s](http://blog.harrisonxi.com/%s/%s/%s.html)\n' % (match.group(3), year, month, match.group(3))
			indexContent = indexContent + '\n[%s](/%s/%s/%s.html)\n' % (match.group(3), year, month, match.group(3))
	# 补全文件尾内容并写入
	indexContent = indexContent + '\n------\n\n© 2017 苹果梨　　首页　　[关于](/about.html)　　[GitHub](https://github.com/HarrisonXi)　　[Email](mailto:gpra8764@gmail.com)\n'
	file = open('README.md', 'w')
	file.write(readmeContent)
	file.close()
	file = open('_pages/index.md', 'w')
	file.write(indexContent)
	file.close()

makeIndex(os.path.join(os.getcwd(), '_posts'))
print('Index is generated.')
