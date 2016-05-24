#JT 2016 - SMTG publication script, using ADS library (found on github)
from __future__ import print_function, division

import ads
import sys
import numpy
import unicodedata
import os.path
from StringIO import StringIO
from time import localtime

# ADS needs a token - this one is for jwt104@googlemail.com so be warned!
ads.config.token = 'zmmgkG86fM0hBeBjoOJicrr5GegJWe69vJ5ULDNd'

#simple function to read in a file
def load(fname):
    ''' load the file using std open'''
    f = open(fname,'r')

    data = []
    for line in f.readlines():
        data.append(line.replace('\n','').split(';'))

    f.close()

    return data

#simple function to compare authors with a list and return a hyperlink if a match found.
def compareauthor(name,sfile):
    '''compare author with SMTG grp members and return link if matched'''    
    assert type(name) == unicode, 'name must be unicode string'
    assert type(sfile) == str, 'staff filename must be a string'
    
    if os.path.exists(sfile): staff=load(sfile)
    
    found=0
    for people in staff:
        nom=','.join(people[2:3])[2:-1]
        if  nom == name.encode("utf-8"):
            #print('FOUND'),
            found=1
            jsthing=''.join(people[4:])
            #print(jsthing[1:]),
            linktoreturn = '<a href={0}>{1}</a>'.format(jsthing[1:],name)
            type(linktoreturn)
            #print(linktoreturn),
            #linktoreturn="<a href=\""+''.join(people[7:])+">"
            #linktoreturn=linktoreturn+name+"</a>"

    if found == 0:
        linktoreturn=name
    
    linktoreturn=u'{0}; '.format(linktoreturn)
            
    return linktoreturn

#simple function to output basic html table of correctly formatted authors and titles of SMTG pubs
def write_table(tlist,alist, filename,stfile):
    '''output simple html table containing list of recent SMTG pubs and authors'''
    assert type(tlist) == list, 'titlelist must be list of titles'
    assert type(alist) == list, 'authorlist must be list of authors'
    assert len(tlist) == len(alist), 'author and title list must be same length'
    assert type(filename) == str, 'name must be string'
    assert type(stfile) == str, 'stafflist file must be a string'
    
    target = open(filename, 'w')
    target.truncate()
    
    #pretty_author_name = lambda author: author.split(",")[0] + author.split(",")[1].strip()[1] + "."
    my_string = '' 
    target.write('<HTML><head></head><body>')
    target.write('<table class="staff" style="border-collapse:collapse;">')
    target.write("\n")
    target.write('<tr><th class="top">Author(s)</th><th class="top">Title</th></tr>')
    target.write("\n")
    for title, authors in zip(tlist, alist):    
    #for paper in titlelist:
        target.write('<tr><td>')
        target.write("\n")
        for author in authors:
            temp=compareauthor(name=author, sfile=stfile)
            target.write(temp.encode('ascii', 'xmlcharrefreplace'))
        
	target.write("\n")
        target.write('</td><td>')
        #target.write(my_string.join(title))
        target.write(' '.join(title).encode('ascii', 'xmlcharrefreplace'))
        target.write('</td></tr>')
        target.write("\n")
    
    target.write('</table></body></HTML>')
    target.close()

#main prog
if __name__ == "__main__":
    print('SMTG PUBLICATION SCRIPT (JT 2016)')
    print("-------")
    #first check the date and rip out the current month/year
    now = localtime()
    year, month = (now.tm_year, now.tm_mon - 1)
    if 1 > month: year, month = (year - 1, month)
    print('Querying Year/Month {0} (in month {1})'.format(year, month)),
    print(),

    #query the location of the current staff list
    staffloc='../staff_current.txt'
    if os.path.exists(staffloc):
    	staff=load(staffloc) 
    else:
        print('NO FILE FOUND AT', staffloc)	
	exit()
	
    outfile='./test.html'

    authlist=[]
    titlelist=[]

    for person in staff:
        #glue together the peoples name in stafflist
        eachname=','.join(person[2:3])[2:-1]
        # Query ADS for author, institute, pub date, database...
        query = ads.SearchQuery( q='author:\"{0}\" pubdate:{1}         aff:(\"University of St Andrews\") property:refereed          database:("astronomy" OR "physics")'.format(eachname, year),
        #fl=['id', 'first_author', 'year', 'bibcode', 'identifier', 'author','title'],
        fl=['author','title'])

        query.execute()
        #count the number of pubs each person has (so far)
        num = int(query.response.numFound)
        print("{person} had {num} publications in {year}".format(person=eachname, num=num, year=year))

        #if anything published, then add that to the list
        if num > 0:
            for n in query:
                #avoid multiple instances of same paper
                if n.title not in titlelist:
                    titlelist.append(n.title)
                    authlist.append(n.author)
                #else:
                    #print('matched publication, ignoring..')
    #list is done, so now write out the table, JOB DONE.
    write_table(tlist=titlelist,alist=authlist,filename=outfile, stfile=staffloc)    
    print("-------")
    print('DONE')
    print('')
