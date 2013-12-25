from bs4 import BeautifulSoup
from time import sleep
import urllib2,os,shutil
import pickle,urlparse
import re

bdFormula = 'http://www.cc98.org/list.asp?boardid=%s&page=%s'
siteURL = 'http://www.cc98.org/'
pageRange = 2

def boardCrawler(boardID,urlFilter,pageRange):
	thrdList=[]
	for pid in range(1,pageRange+1):
		print 'Processing Page #'+str(pid)
		bdURL = bdFormula%(boardID,pid)
		print bdURL
		bdContent = urllib2.urlopen(bdURL).read()
		tpidList = re.compile('topic_[\d]+').findall(bdContent)# Topic ID list

		bbcnt = BeautifulSoup(bdContent) # BeautifulSoup Content
		for tpid in tpidList:
			tpItem = bbcnt.find('a',id=tpid)
			tpURL = tpItem.get('href')
			if urlFilter(tpURL,boardID):
				thrdList.append([tpid,tpURL,tpItem.text])
		sleep(1)
	return thrdList

def mp3Crawler(tpList):
	allMp3List = []
	#itp = tpList[8]
	for itp in tpList[3:]:
		tURL = urlparse.urljoin(siteURL,itp[1])
		print itp[2].encode('utf8')
		itp[2] = itp[2].replace('\n','')
		tpContent = urllib2.urlopen(tURL)
		bstpContent = BeautifulSoup(tpContent)
		lzContent = bstpContent.find(id='ubbcode1').text.encode('utf-8')
		#print lzContent
		tMp3URLSet = re.compile('\[mp3\](http://.*?|MicFileDown.*?)\[/mp3\]').findall(lzContent)
		if len(tMp3URLSet) >0:
			for imp3URL in tMp3URLSet:
				if imp3URL.startswith('MicFileDown'):
					imp3URL = urlparse.urljoin(siteURL,imp3URL)
				print 'MP3 Found: '+imp3URL
				allMp3List.append([itp[2],imp3URL])
		#break
		sleep(1)
	return allMp3List
		#(itp,mp3List,lzContent)

def testReg():
	url = 'http://www.cc98.org/dispbbs.asp?boardID=314&ID=4305678&page=1' #'http://www.cc98.org/dispbbs.asp?boardID=314&ID=4302014&page=1'
	data = urllib2.urlopen(url).read()
	bsdata = BeautifulSoup(data)
	lzContent = bsdata.find(id='ubbcode1').text.encode('utf8')
	print re.compile('\[mp3\]((http://|MicFileDown).*?)\[/mp3\]').findall(lzContent) #\[mp3\](http://|MicFileDown.*?)\[/mp3\]'



def urlFilter(tpURL,boardID):
	bdID = re.compile('\d+').findall(tpURL)[0]
	if bdID == boardID:
		return True
	else:
		return False

def dumpToJson(allMp3List):
	itemCNT = 0
	print 'Total: '+ str(len(allMp3List))
	oFile = open('playList.json','w')
	oFile.write('playList = [\n')
	for imp3Info in allMp3List:
		# print imp3Info
		if itemCNT>0:
			oFile.write(',')
		oJItem = '{title:"%s",mp3:"%s"}\n'%(imp3Info[0],imp3Info[1])
		oFile.write(oJItem.encode('utf8'))
		itemCNT = itemCNT+1
	oFile.write('];')

def musicCrawler():
	boardID = '314'
	# topicList = boardCrawler(boardID,urlFilter,pageRange)
	# pickle.dump(topicList,open('thrdList.p','wb'))
	topicList = pickle.load(open('thrdList.p','rb')) # topicList contains [topicid, topicURL, topic title]
	#print len(topicList)
	allMp3List = mp3Crawler(topicList)
	pickle.dump(allMp3List,open('allMp3List.p','wb'))
	#allMp3List = pickle.load(open('allMp3List.p','rb')) # [musicTitle, musicURL]
	dumpToJson(allMp3List)

	#ulist2json(allMp3List)

def testURL():
	url = 'http://www.cc98.org/MicFileDown.asp?id=3319'
	
	print urllib2.urlopen(url).read()

if __name__=='__main__':
	#testReg()
	#testURL()
	# ss = u'\u3010\u7ffb\u5531\u3011\u300a\u6b64\u95f4\u7684\u5c11\u5e74\u300b\u4e3b\u9898\u66f2\u2014\u8f6c\u8eab\u4e4b\u95f4'
	# print ss.encode('utf8','ignore')
	musicCrawler()