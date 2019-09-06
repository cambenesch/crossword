import httplib2, re

""" helper((a,b)) returns a tuple of clues linked to a tuple list [(x,y),...] where
    x is the predicted answer and y is the probability that it
    is correct for each clue"""
def helper(tup):
    x=tup[0].strip()
    x=x.replace(' ','+')
    y=tup[1].strip()
    y=y.replace('?',"%3F")
    pat = re.compile('<div class="solver-cell">(.+?)</div>')
    http = httplib2.Http()
    headers, body = http.request("https://www.dictionary.com/e/crosswordsolver/?query="+x+"&pattern=" + y + "&l=any")
    seclist = pat.findall(body.decode('ISO-8859-1'))
    tuplist = []
    temptup = ("","")
    for i in range(0,len(seclist)):
        if i%2==0:
            temptup = (seclist[i],0)
        else:
            thisone = seclist[i]
            temptup = (temptup[0],int(thisone[:len(thisone)-1]))
            tuplist = tuplist + [temptup]
    return tuplist
        

""" get_answers(clues) returns a dictionary of crossword number linked to tuples (x,y) where
    x is the predicted answer and y is the probability that it
    is correct for each clue. REQUIRES: clues is a dictionary {question # : (clue,length)}"""
def get_answers(clues):
    keys = clues.keys()
    acc_dict = {}
    for key in keys:
        acc_dict[key] = helper(clues[key])
    return acc_dict


print(get_answers({'1' : ("like a cat","?????"), '2' : ("women with kids","???")}))