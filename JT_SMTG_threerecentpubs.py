
# coding: utf-8

# In[2]:

from __future__ import print_function, division
import ads
import sys
import numpy
import unicodedata
import os.path
import re
import string
from StringIO import StringIO
from time import localtime
from tempfile import mkstemp
from shutil import move
from os import remove, close


# In[3]:

# ADS needs a token - this one is for jwt104@googlemail.com so be warned!
ads.config.token = 'zmmgkG86fM0hBeBjoOJicrr5GegJWe69vJ5ULDNd'


# In[4]:

#simple function to read in a file
def load(fname):
    ''' load the file using std open'''
    f = open(fname,'r')

    data = []
    for line in f.readlines():
        data.append(line.replace('\n','').split(';'))

    f.close()

    return data


# In[11]:

#complex function to steal javascript string from stafflist file and append/update with latest pubs (if any)
def updatepubs(oldstaffloc,newstaffloc):
    ''' read in staff data and append latest ads pub info'''

    #first check the date and rip out the current month/year
    now = localtime()
    print, now
    year, month = (now.tm_year, now.tm_mon)
    if 1 > month: year, month = (year - 1, month)
    print('Querying Year/Month {0} (in month {1})'.format(year, month)),
    print(),

    #query the location of the current staff list
    #staffloc='../staff_current_temp.txt'
    if os.path.exists(staffloc):
        staff=load(staffloc)
    else:
        print('NO FILE FOUND AT', staffloc)	
        exit() 
    
    nstaff=len(staff)
    staffcount=0
    
    with open(oldstaffloc, 'r') as old_file:
        with open(newstaffloc,'w') as new_file:
            for person in staff[0:29]:#remember that peter and bernie do NOT have a javascript thing.
                staffcount +=1
                newdatalist=[]
                #glue together the peoples name in stafflist
                eachname=','.join(person[2:3])[2:-1]
                # Query ADS for author, institute, pub date, database...
                papers=list(ads.SearchQuery(sort="date desc", fl=['author','title','doi', 'bibcode'],                                             q='author:\"{0}\" aff:("University of St Andrews"                                             OR "National Astronomical Observatory of Japan")                                             property:refereed database:("astronomy" OR "physics")'.format(eachname)))
                if len(papers) >= 3:
                    for n in papers[0:3]:
                        newdatalist.append(str(n.doi).encode('ascii')[3:-2])
                        newdatalist.append(str(n.bibcode).encode('ascii'))
                else:
                    for n in papers:
                        newdatalist.append(str(n.doi).encode('ascii')[3:-2])
                        newdatalist.append(str(n.bibcode).encode('ascii'))
                
                print('staff member {0}'.format(staffcount))
                print('{0} - {1} papers'.format(eachname, len(papers)))
                linecount=0
                old_file.seek(0)
                for line in old_file:
                    linecount+=1
                    #print('linecount {0} - staffcount {1}'.format(linecount, staffcount))
                    if linecount == staffcount:
                        #print(line)
                        data = []
                        data.append(line.replace('\n','').split(';'))
                        #print('; '.join(data[0][-7:-1]))
                        #print('replace with')
                        #print('; '.join(newdatalist))
                        #print(data[0][4])
                        temp=data[0][4].split(",")
                        #print(temp)
                        keep=temp[0:4]
                        tkeep=''
                        if len(newdatalist)== 6:
                            tkeep=string.replace(keep[0],'createP','createP3')
                        if len(newdatalist)== 4:
                            tkeep=string.replace(keep[0],'createP','createP2')
                        if len(newdatalist)== 2:
                            tkeep=string.replace(keep[0],'createP','createP1')
                        if len(newdatalist)== 0:
                            tkeep=keep[0]                       
                        keep[0]=tkeep       
                        keep.append(temp[-1].split(")")[0])
                        needcomma= ', ' if len(newdatalist)>=1 else ''
                        newtemp=', '.join(front for front in keep)+ needcomma +                        ', '.join("'" + item + "'" for item in newdatalist)+')"'
                        data[0][4]=newtemp
                        data[0][:].append('\n')
                        newline=';'.join(data[0][:])+'\n'
                        new_file.write(newline)
                        
            


# In[12]:

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


# In[13]:

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
        target.write(str(title)[3:-2].encode('ascii', 'xmlcharrefreplace'))
        target.write('</a>')
        target.write('</td></tr>')
        target.write("\n")
    
    target.write('</table></body></HTML>')
    target.close()


# In[18]:

#main prog
if __name__ == "__main__":
    print('SMTG recent pubs script (JT 2016)')
    print("-------")
    
    staffloc='../staff_current_temp.txt'
    outfile='../staff_current_temp2.txt'
    
    updatepubs(staffloc, outfile)

    #updated to include NAOJ articles for patrick
    #10.1017/S0022377816000519 is Oliver's most recent pub (see also fiona, thomas), but ADS omits DOI.
    #jonathan's 2015 paper ,'10.1080/03091929.2015.1081188','2015GApFD.109..524H' is ignored by ADS

    print("-------")
    print('DONE: output to {0}'.format(outfile))
    print('-------')
    print('')



