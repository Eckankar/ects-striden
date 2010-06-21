#!/usr/bin/env python

import re
import itertools
import operator
import getpass
import urllib2, cookielib
from urllib import urlencode

class punktKU():
    # URL constants
    OLD_LOGIN_URL='https://www2.adm.ku.dk/portal/login/loginProces.asp'
    NEW_LOGIN_URL='https://www2.adm.ku.dk/portal/login/newLoginProces.asp'
    LOGOUT_URL='https://www2.adm.ku.dk/portal/logud.asp'
    MENU_URL='https://www2.adm.ku.dk/portal/LeftMenu/RegionalMenu.asp?RegionalMenu=0'
    SESSION_ACTIVATE_URL='https://www2.adm.ku.dk/portal/default.asp?RegionalMenu=95&PageID=179&'
    ECTS_URL='https://www2.adm.ku.dk/selv/pls/prt_www5.res_renset?p_print=true&p_nyeste=false&p_flere_skala=true&p_renset=true&'
    CLASSES_URL='https://www2.adm.ku.dk/selv/pls/prt_www22.hold_oversigt?'

    def __init__(self, user, password, oldLogin = False):
        # Initializes cookie handler
        jar = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(jar)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        self._login(user, password, oldLogin)
        self._get_p_session_id()

    def __del__(self):
        self._logout()

    def _login(self, user, password, oldLogin):
        # TODO: handle errors
        if oldLogin:
            logindata = {'ssousername': user, 'password': password}
            urllib2.urlopen(punktKU.OLD_LOGIN_URL, urlencode(logindata)).read()
        else:
            logindata = {'username': user, 'password': password}
            urllib2.urlopen(punktKU.NEW_LOGIN_URL, urlencode(logindata)).read()

        self._isLoggedIn = True

    def _get_p_session_id(self):
        sessionHTML = urllib2.urlopen(punktKU.MENU_URL).read()
        self._session_id = re.search(r'p_session_id=[^"&]*', sessionHTML).group(0)

        # For some reason punkt.KU wants us to activate the session ID by going to this page first
        urllib2.urlopen(punktKU.SESSION_ACTIVATE_URL + self._session_id).read()

    def _logout(self):
        if self._isLoggedIn:
            urllib2.urlopen(punktKU.LOGOUT_URL).read()
            self._isLoggedIn = False

    def getECTSData(self):

        Classes = self.getClasses()

        # Gets the page with the ECTS data
        ECTShtml = urllib2.urlopen(punktKU.ECTS_URL + self._session_id).read()


        # Parsing data
        ECTSdata = [(l.split('\"')[3][2:], l.split('\"')[5]) for l in ECTShtml.splitlines() if l.startswith('    <input type="hidden" name="p_')]
        ECTSdictionaries = [dict(ECTSdata[k*5:k*5+5]) for k in range(len(ECTSdata) // 5)]

        for d in ECTSdictionaries:
            # Converts the ects points to a proper number
            d['ects_p'] = float(d['ects_p'])

            takenClasses = [(year,block) for (year,block,name) in Classes if name.startswith(d['tekst'])]

            if len(takenClasses) == 0:
                # punktKU does not give any information about taken classes
                # so just guess which block it is from the date
                d['guess'] = True

                month = int(d['dato'][2:4])
                year = int(d['dato'][4:])


                if month >= 8:
                    d['year'] = year
                    d['block'] = 1
                else:
                    monthToBlock = [2,2,2,3,3,4,4]
                    d['year'] = year-1
                    d['block'] = monthToBlock[month]

            else:
                d['guess'] = False
                d['year'], d['block'] = max(takenClasses)

            
            # Try to guess when the course ended
            if d['ects_p'] < 10 or d['block'] in [2,4]:
                # Semesters doesn't overlap 
                d['blockduration'] = 1
            else:
                # TODO: make better estimate, especially in known differences from this rule
                d['blockduration'] = 2


        return ECTSdictionaries 

    def getClasses(self):
        # Gets the page with the class data
        ClassesHTML = urllib2.urlopen(punktKU.CLASSES_URL + self._session_id).read()

        # Parsing data
        ClassesData = [l.split('>')[1] for l in ClassesHTML.splitlines() if l.startswith('      <td class="FastFontSize">')]

        Classes = []

        # Adds every taken class to the list
        for k in range(len(ClassesData) // 3):
            curClass = ClassesData[3*k+1]
            semester = ClassesData[3*k]
            year = int('20' + semester[3:5])
            block = int(semester[1])

            Classes.append((year,block,curClass))

        Classes.sort()

        return Classes

    def printBattleFormat(self, comments = True):

        # Gets course data into a format suitable for sorting and grouping
        ECTSdata = [((d['year'], d['block'], d['blockduration']), d['ects_p'], d['tekst']) for d in self.getECTSData()]
        ECTSdata.sort()

        grouped = itertools.groupby(ECTSdata, operator.itemgetter(0))

        curyear = 0

        # Iterates through the grouped data
        for (year, block, blockduration), v in grouped:

            v = list(v)

            names = [c[2] for c in v]
            ects = sum([c[1] for c in v])

            if curyear < year:
                curyear = year
                yearstring = str(year) + ","
            else:
                yearstring = "-,   "

            if blockduration == 1:
                blockstring = str(block) + ":"
            else:
                blockstring = "s" + str(block // 2) + ":"

            print yearstring, blockstring, ects,

            if comments:
                print "#", reduce(lambda x,y : x + ", " + y, names)
            else:
                print


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print "Usage:"
        print sys.argv[0], "nummerplade", "[--disable-comments]"
        print
        print "or"
        print
        print sys.argv[0], "cpr-nummer", "[--disable-comments]"
        print
    else:
        if sys.argv[1].isdigit():
            p = punktKU(sys.argv[1], getpass.getpass(), True)
        else:
            p = punktKU(sys.argv[1], getpass.getpass(), False)

        if len(sys.argv) >= 3 and sys.argv[2] == "--disable-comments":
            p.printBattleFormat(False)
        else:
            p.printBattleFormat()

