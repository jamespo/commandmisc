#!/usr/bin/env python

# pagechange.py - quick script to check if page has changed
# (eg - for price checking)

# .product-prices .oldPrice
# http://www.massimodutti.com/gb/two-tone-bluchers-with-laces-c1313028p6954836.html
# //*[@id="product-info"]/div/div[2]/div[1]/div/div/p[2]

import os
import os.path
import re
import cPickle as pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from optparse import OptionParser

SAVEDIR = os.path.join(os.path.expanduser('~'), '.pagechange')


class Page(object):

    def __init__(self, url=None, xpath=None, filename=None):
        self.url = url
        self.xpath = xpath
        self.oldmatch = ''
        self.match = ''
        self.filename = filename
        self.title = ''

    def save(self):
        '''Pickle Page object'''
        if self.filename is None:
            # create alphanumeric filename from URL
            self.filename = re.sub('(^https?://|[\W_]+)', '', self.url) + '.pk'
        fullfilename = os.path.join(SAVEDIR, self.filename)
        # print fullfilename
        with open(fullfilename, 'wb') as picklefile:
            pickle.dump(self, picklefile)

    def __str__(self):
        # return self.match.encode('utf-8')
        return "Title: %s\nOld: (%s) New: (%s)\nURL: %s" \
            % (self.title.encode('utf-8'), self.oldmatch.encode('utf-8'),
               self.match.encode('utf-8'), self.url)

    def load(self):
        with open(os.path.join(SAVEDIR, self.filename), 'rb') as pfile:
            a = pickle.load(pfile)
            # copy pickle object into self
            self.__dict__ = a.__dict__.copy()

            
class PageChange(object):

    def __init__(self):
        '''instantiate webdriver'''
        #self.driver = webdriver.Firefox()
        self.driver = webdriver.Chrome()
        self.waittime = 5
        self.xpmatch = None
        
    def check(self, page):
        '''return content in page matching xpath'''
        self.driver.get(page.url)
        self.driver.implicitly_wait(self.waittime)
        # assert "Python" in driver.title
        self.xpmatch = self.driver.find_element(By.XPATH, page.xpath)
        return self.xpmatch.text

    def update_page(self, page):
        '''updates page object'''
        changed = (self.xpmatch.text != page.match)
        if changed:
            page.oldmatch = page.match
            page.match = self.xpmatch.text
            page.title = self.driver.title
            page.save()
        return changed

def get_options():
    '''parse CLI options'''
    parser = OptionParser()
    parser.add_option("-u", help="url", dest="url")
    parser.add_option("-x", help="xpath", dest="xpath")
    parser.add_option("-m", help="mode (add|check|list)", dest="mode",
                      default="add")
    (options, args) = parser.parse_args()
    return (options, args)


def get_all_checks():
    checkfiles = os.listdir(SAVEDIR)
    checks = []
    for cf in checkfiles:
        check = Page(filename=cf)
        check.load()
        checks.append(check)
    return checks
                  

def list_pages():
    for check in get_all_checks():
        print check


def add_page(options):
    p = Page(options.url, options.xpath)
    pc = PageChange()
    try:
        pc.check(p)
    except:
        pass
    pc.update_page(p)
    print p
    pc.driver.close()


def main():
    (options, args) = get_options()
    if options.mode == 'add':
        if None in (options.url, options.xpath):
            print "No url/xpath provided"
        else:
            add_page(options)
    elif options.mode == 'list':
        list_pages()

if __name__ == '__main__':
    main()
