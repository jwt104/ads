
# coding: utf-8

# In[28]:

from __future__ import print_function, division


# In[29]:

import ads
import sys
import numpy
import unicodedata
import os.path
from StringIO import StringIO
from time import localtime


# In[30]:

# ADS needs a token - this one is for jwt104@googlemail.com so be warned!
ads.config.token = 'zmmgkG86fM0hBeBjoOJicrr5GegJWe69vJ5ULDNd'


# In[31]:

#simple function to read in a file
def load(fname):
    ''' load the file using std open'''
    f = open(fname,'r')

    data = []
    for line in f.readlines():
        data.append(line.replace('\n','').split(';'))

    f.close()

    return data


# In[32]:

# function to compare name against staff list and add hyperlink if match found
def compareauthor(name,sfile):
    '''compare author with SMTG grp members and return link if matched'''    
    assert type(name) == unicode, 'name must be unicode string'
    assert type(sfile) == str, 'staff filename must be a string'
    
    if os.path.exists(sfile): staff=load(sfile)
    
    found=0
    for people in staff:
        nom=','.join(people[2:3])[2:-1]
        if len(people[0].split()) == 3:
            altnom=''.join(people[0].split(' ')[2:3])+', '+' '.join(people[0].split(' ')[0:2])
        else:
            altnom=', '.join(people[0].split(' ')[::-1])
        if  nom == name.encode("utf-8"):
            #print('FOUND'),
            found=1
            jsthing=''.join(people[4:])
            linktoreturn = '<a href={0}>{1}</a>'.format(jsthing[1:],name)
            type(linktoreturn)
            #fine, thats the normal short form name, what about full name?

        if  found==0 and altnom == name.encode("utf-8"):
            #print('FOUND'),
            found=1
            jsthing=''.join(people[4:])
            linktoreturn = '<a href={0}>{1}</a>'.format(jsthing[1:],altnom)
            type(linktoreturn)
            

    if found == 0:
        linktoreturn=name
    
    linktoreturn=u'{0}; '.format(linktoreturn)
            
    return linktoreturn


# In[33]:

#simple function to output basic html table of correctly formatted authors and titles of SMTG pubs
def write_table(tlist,alist, dlist, filename,stfile):
    '''output simple html table containing list of recent SMTG pubs and authors'''
    assert type(tlist) == list, 'titlelist must be list of titles'
    assert type(alist) == list, 'authorlist must be list of authors'
    assert type(dlist) == list, 'doilist must be list of authors'
    assert len(tlist) == len(alist), 'author and title list must be same length'
    assert type(filename) == str, 'name must be string'
    assert type(stfile) == str, 'stafflist file must be a string'
    
    target = open(filename, 'w')
    target.truncate()
    
    my_string = '' 
    target.write('<HTML><head></head><body>')
    target.write('<table>')
    target.write("\n")
    for title, authors, doi in zip(tlist, alist, dlist):    
    #for paper in titlelist:
        target.write('<tr><td>')
        target.write("\n")
        for author in authors:
            temp=compareauthor(name=author, sfile=stfile)
            target.write(temp.encode('ascii', 'xmlcharrefreplace'))
        
        target.write("\n")
        target.write('</td><td>')
        target.write('<a href=http://dx.doi.org/')
        target.write(str(doi).encode('ascii')[3:-2])
        target.write('>')
        target.write(str(title).encode('ascii', 'xmlcharrefreplace')[3:-2])
        target.write('</a>')
        target.write('</td></tr>')
        target.write("\n")
    
    target.write('</table></body></HTML>')
    target.close()


# In[35]:

#main prog
if __name__ == "__main__":
    print('SMTG PUBLICATION SCRIPT (JT 2016)')
    print("-------")
    #first check the date and rip out the current month/year
    now = localtime()
    print, now
    year, month = (now.tm_year, now.tm_mon)
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
    doilist=[]
    
    for person in staff:
        #glue together the peoples name in stafflist
        eachname=','.join(person[2:3])[2:-1]
        # Query ADS for author, institute, pub date, database...
        query = ads.SearchQuery(  fl=['author','title','doi'], q='author:\"{0}\" pubdate:{1}         aff:(\"University of St Andrews\") property:refereed          database:("astronomy" OR "physics")'.format(eachname, year),
        #fl=['id', 'first_author', 'year', 'bibcode', 'identifier', 'author','title'],
        rows=5 )
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
                    doilist.append(n.doi)
                #else:
                    #print('matched publication, ignoring..')
    #list is done, so now write out the table, JOB DONE.
    
    write_table(tlist=titlelist,alist=authlist,dlist=doilist,filename=outfile, stfile=staffloc)    
    print("-------")
    print('DONE: output to {0}'.format(outfile))
    print('-------')
    print('')


# In[14]:

temp=str(doilist[0])[1:-1]
print(temp.encode("ascii"))
print(temp[2:-1])


# In[85]:

y=[s.encode('ascii', 'ignore') for s in doilist]


# In[77]:

type(doilist)


# In[24]:

print(authlist)


# In[ ]:



