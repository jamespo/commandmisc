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
from pyvirtualdisplay import Display

SAVEDIR = os.path.join(os.path.expanduser('~'), '.pagechange')


class Page(object):

    def __init__(self, savedir, url=None, xpath=None, filename=None):
        self.savedir = savedir
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
        fullfilename = os.path.join(self.savedir, self.filename)
        # print fullfilename
        with open(fullfilename, 'wb') as picklefile:
            pickle.dump(self, picklefile)

    def __str__(self):
        # return self.match.encode('utf-8')
        return "Title: %s\nOld: (%s) New: (%s)\nURL: %s" \
            % (self.title.encode('utf-8'), self.oldmatch.encode('utf-8'),
               self.match.encode('utf-8'), self.url)

    def load(self):
        with open(os.path.join(self.savedir, self.filename), 'rb') as pfile:
            a = pickle.load(pfile)
            # copy pickle object into self
            self.__dict__ = a.__dict__.copy()

            
class PageChange(object):

    def __init__(self, browser):
        '''instantiate webdriver'''
        if browser == 'firefox':
            self.driver = webdriver.Firefox()
        elif browser == 'chrome':
            self.driver = webdriver.Chrome()
        else:
            raise ValueError('No valid webdriver found')
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
    parser.add_option("-b", help="browser", dest="browser",
                      default="firefox")
    parser.add_option("-d", help="savedir", dest="savedir",
                      default=os.path.join(os.path.expanduser('~'), '.pagechange'))
    (options, args) = parser.parse_args()
    return (options, args)


def get_all_checks(savedir):
    checkfiles = [cf for cf in os.listdir(savedir) if cf[-3:] == '.pk']
    checks = []
    for cf in checkfiles:
        check = Page(savedir=savedir, filename=cf)
        check.load()
        checks.append(check)
    return checks
                  

def list_pages(savedir):
    for check in get_all_checks(savedir):
        print check
        print ''


def check_pages(options):
    pc = PageChange(browser=options.browser)
    for check in get_all_checks(options.savedir):
        pc.check(check)
        if pc.update_page(check):
            # changed
            print check
    pc.driver.close()

def add_page(options):
    p = Page(options.savedir, options.url, options.xpath)
    pc = PageChange(browser=options.browser)
    try:
        pc.check(p)
    except:
        pass
    pc.update_page(p)
    print p
    pc.driver.close()

def virt_display(function, options):
    display = Display(visible=0, size=(800, 600))
    display.start()
    function(options)
    display.stop()

def main():
    (options, args) = get_options()
    if options.mode == 'add':
        if None in (options.url, options.xpath):
            print "No url/xpath provided"
        else:
            # TODO: add visible switch for add_page(options)
            virt_display(add_page, options)
    elif options.mode == 'list':
        list_pages(savedir=options.savedir)
    elif options.mode == 'check':
        # TODO: add visible switch
        virt_display(check_pages, options)

if __name__ == '__main__':
    main()
