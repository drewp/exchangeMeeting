import os, getpass, urllib
from BeautifulSoup import BeautifulSoup
from rdflib.Graph import Graph
import twill
import twill.commands as C
from rdflib import URIRef, Namespace, Literal

EM = Namespace("http://bigasterisk.com/exchangeMeeting/")

"""
http://www.holovaty.com/code/weboutlook/0.1/scraper.py
doesn't look like the same urls for my version, and it does email not calendar.

http://blogs.msdn.com/tmeston/archive/2004/12/07/277470.aspx
http://blogs.msdn.com/tmeston/archive/2004/06/12/154068.aspx
seems old


new-style OWA, here's a single url for login and day:
  https://owa.dwextra.com/owa/auth/logon.aspx?url=https://owa.dwextra.com/owa/%3Fae=Folder%26t=IPF.Appointment%26yr=2007%26mn=11%26dy=28


error handling is poor. even a wrong username doesn't make an exception.

"""

def _getCalendar(config, top, ymd):
    b = twill.get_browser()
    b.set_agent_string("Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7) Gecko/20040616")

    val = lambda p: config.value(top, p)

    server = val(EM['server']).rstrip('/')
    returnParams = urllib.urlencode(dict(ae="Folder", t="IPF.Appointment",
                                         yr=ymd[0], mn=ymd[1], dy=ymd[2]))
    returnUrl = "%s/owa/?%s" % (server, returnParams)
    b.go("%s/owa/auth/logon.aspx?%s" % (server,
                                        urllib.urlencode(dict(url=returnUrl))))
    
    C.formvalue(1, "username", val(EM['user']))
    C.formvalue(1, "password", val(EM['password']))
    C.submit(8)

    return b.get_html()


def getCalendar(config, top, ymd):
    """tries to get the calendar data two times, since sometimes I'm
    getting failures that fix after one retry"""
    try:
        return _getCalendar(config, top, ymd)
    except twill.errors.TwillAssertionError, e:
        return _getCalendar(config, top, ymd)

def parse(html):
    """returns meetings in the order they're seen on the page"""
    soup = BeautifulSoup(html)
    meetings = []
    for h1 in soup.findAll(attrs={'class' : 'bld'}):
        a = h1.contents[0]
        title = a['title']
        #print a.contents[0]
        times, desc = title.split(' , ', 1)
        start, end = times.split(' - ')

        meetings.append((start, end, desc))
        
    return meetings

if __name__ == '__main__':
    if 0:
        config = Graph()
        config.parse("config.n3", format="n3")
        top = URIRef("file://" + os.path.abspath("config.n3"))
        passwd = getpass.getpass("Password for %s: " % config.value(top, EM['user']))
        config.add((top, EM['password'], Literal(passwd)))

        cal = getCalendar(config, top, (2009, 1, 26))
        open("owa", "w").write(cal)
    else:
        cal = open("owa").read()
        print parse(cal)

