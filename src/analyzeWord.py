import re
gblLine1 = re.compile("^<SYNC\s+\w+=[0-9]+><P Class=\w+>", re.I)
gblSyncPos = re.compile("Start=[0-9]+", re.I)
gblClassName = re.compile("Class=\w+", re.I)
gblWordList = { }
gblWordDictList = { }
gblWordExcludeList = { }
gblRet = {"TYPE":0,   ## Type line
	       "TEXT":"",
	       "CLASS":"",
	       "START":0   ## Sync Start Position
	     }

def analyzeLine(t) :
	global gblRet
	ret = gblRet.copy()
	# find <SYNC Start=0000><P Class=KRCC>       
	flist = gblLine1.findall(t)

	if len(flist)>0 :
		# find Start=n
		StartString = gblSyncPos.search(flist[0]).group()
		ret["START"] = int(StartString[6:])

		# find class
		ClassName = gblClassName.search(flist[0]).group()
		ret["CLASS"] = ClassName[6:]

		# find text
		ret["TEXT"] = t[len(flist[0]):].replace("\r","").replace("\n","")
	else :
		return t

	return ret

def analyzeWord(dic) :
	global gblWordList
	global gblWordExcludeList
	textline = dic["TEXT"].replace("\r"," ").replace("\n"," ").replace("."," ").replace("<BR>"," ").replace("<br>"," ").replace("?"," ").replace(","," ")
	for w in textline.split(" ") :
		w = w.lower()
		if w.isalpha() :
			if not gblWordExcludeList.has_key(w) :
				if gblWordList.has_key(w) :
					gblWordList[w] = gblWordList[w] + 1
				else :
					gblWordList[w] = 1
	#print textline


def loadDictionary(fname, bNotExclude) :
	global gblWordDictList
	global gblWordExcludeList
	f = open(fname, 'r')
	for ln in f.xreadlines() :
		ln = ln.replace("\r","").replace("\n","")
		if ln is not "" :
			lvl = 1
			if ln[0]=="#" :
				if ln == "#Level0" :
					lvl = 0
				elif ln == "#Level1" :
					lvl = 1
				elif ln == "#Level2" :
					lvl = 2
				elif ln == "#Level3" :
					lvl = 3

			elif ln[0]=="*" :
				gblWordExcludeList[ln[1:]] = lvl
			else :
				if not bNotExclude :
					gblWordExcludeList[ln] = lvl
				else :
					gblWordDictList[ln] = lvl


# Load basic word
loadDictionary("word_basic.dic", False)

# Load Word List
loadDictionary("word_list.dic", True)

f = open('sample.smi','r')
current = gblRet.copy()
bFindBody = False
for lns in f.xreadlines() :
	if "</BODY" in lns :
		bFindBody = False
	if bFindBody :
		retVal = analyzeLine(lns)
		if type(retVal) is str :
			current["TEXT"] = current["TEXT"] + retVal.replace("\r","").replace("\n","")
		elif type(retVal) is dict :
			analyzeWord(current)
			current = retVal.copy()
	else :
		#print lns
		pass
	if "<BODY" in lns :
		bFindBody = True

analyzeWord(current)

sval = sorted(gblWordList.items(), key=lambda x: x[1], reverse=True)
print sval
print sval[0][0]