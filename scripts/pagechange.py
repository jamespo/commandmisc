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
import tempfile
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import \
    NoSuchElementException, StaleElementReferenceException
from optparse import OptionParser
from pyvirtualdisplay import Display

# default
SAVEDIR = os.path.join(os.path.expanduser('~'), '.pagechange')


class EmptyMatchException(Exception):
    pass


class Page(object):

    def __init__(self, savedir, url=None, xpath=None, filename=None):
        self.savedir = savedir
        self.url = url
        self.xpath = xpath
        self.oldmatch = ''
        self.datetime = ''
        self.match = ''
        self.filename = filename
        self.title = ''

    def save(self):
        '''Pickle Page object (self) and save to disk'''
        if self.filename is None:
            # create alphanumeric filename from URL
            self.filename = re.sub('(^https?://|[\W_]+)', '', self.url) + '.pk'
        fullfilename = os.path.join(self.savedir, self.filename)
        # print fullfilename
        with open(fullfilename, 'wb') as picklefile:
            pickle.dump(self, picklefile)

    def __str__(self):
        '''printable representation of self'''
        # handle missing datetime
        try:
            getattr(self, 'datetime')
        except AttributeError:
            self.datetime = ''
        return "Title: %s\nOld: (%s)   New: (%s)\nChanged: %s\nURL: %s" \
            % (self.title.encode('utf-8'), self.oldmatch.encode('utf-8'),
               self.match.encode('utf-8'), self.datetime, self.url)

    def load(self):
        '''load pickled page object from disk'''
        with open(os.path.join(self.savedir, self.filename), 'rb') as pfile:
            savedir = self.savedir
            a = pickle.load(pfile)
            # copy pickle object into self
            self.__dict__ = a.__dict__.copy()
            # restore savedir
            self.savedir = savedir


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

    @staticmethod
    def dump_source(source):
        '''write source to tempfile & return filename'''
        fh, fname = tempfile.mkstemp(suffix='pchange', text=True)
        os.write(fh, source)
        os.close(fh)
        return fname


    def check(self, page):
        '''return content in page matching xpath'''
        # insert dummy about to wipe referer
        self.driver.get('about:blank')
        self.driver.get(page.url)
        self.driver.implicitly_wait(self.waittime)
        if os.getenv('DEBUG'):
            fname = self.dump_source(encode(self.driver.page_source))
            print 'source html in %s' % fname
        # assert "Python" in driver.title
        self.xpmatch = self.driver.find_element(By.XPATH, page.xpath)
        # cookie cleanup - make optional?
        self.driver.delete_all_cookies()
        return self.xpmatch.text


    def update_page(self, page, forcesave=False):
        '''updates page object - saves if changed or if forcesave = True'''
        #if page.match == '':
        #    raise EmptyMatchException('blank match in %s' % self.driver.title)
        changed = (self.xpmatch.text != page.match)
        if changed or forcesave:
            page.oldmatch = page.match
            page.match = self.xpmatch.text
            page.title = self.driver.title
            page.datetime = time.strftime('%d-%m-%Y %X %Z')
            page.save()
        return changed or forcesave


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
                      default=SAVEDIR)
    parser.add_option("-f", help="force save", dest="forcesave",
                      action="store_true", default=False)
    parser.add_option("-n", help="no headless", dest="noheadless",
                      action="store_true", default=False)
    (options, args) = parser.parse_args()
    return (options, args)


def get_all_checks(savedir):
    '''loads all checks in savedir and returns list'''
    checkfiles = [cf for cf in os.listdir(savedir) if cf[-3:] == '.pk']
    checks = []
    for cf in checkfiles:
        check = Page(savedir=savedir, filename=cf)
        check.load()
        checks.append(check)
    return checks


def list_pages(savedir):
    '''displays all checks in savedir'''
    for check in get_all_checks(savedir):
        print check
        print ''

        
def encode(s, encoding="ascii", errors="ignore"):
    '''custom decode function to ignore errors'''
    return s.encode(encoding=encoding, errors=errors)


def check_pages(options):
    '''run all checks & display changed'''
    pc = PageChange(browser=options.browser)
    for check in get_all_checks(options.savedir):
        try:
            pc.check(check)
            if pc.update_page(check, options.forcesave):
                # changed
                print check
            elif os.getenv('DEBUG'):
                print 'No change for %s' % encode(check.title, 'ascii')
        except (NoSuchElementException, StaleElementReferenceException) as e:
            # print '%s failed - error: %s' % (check.title, str(e))
            print '%s failed - error: %s' % (encode(check.title, 'ascii'), e)
        except EmptyMatchException:
            print "Match returned empty string for %s" % encode(check.title, 'ascii')
    pc.driver.close()


def add_page(options):
    '''add a check'''
    p = Page(options.savedir, options.url, options.xpath)
    pc = PageChange(browser=options.browser)
    try:
        pc.check(p)
        pc.update_page(p)
        print p
    except NoSuchElementException:
        print 'Cannot find match in page - not saving'
    except EmptyMatchException:
        print 'Match returns empty string - not saving'
    pc.driver.close()


# TODO: convert to decorator
def virt_display(function, options):
    '''launch virtual display (for selenium) and run function'''
    display = Display(visible=0, size=(800, 600))
    display.start()
    function(options)
    display.stop()


def main():
    '''check args and run appropriate function'''
    (options, args) = get_options()
    if options.mode == 'add':
        if None in (options.url, options.xpath):
            print "No url/xpath provided"
        else:
            if options.noheadless:
                add_page(options)
            else:
                virt_display(add_page, options)
    elif options.mode == 'list':
        list_pages(savedir=options.savedir)
    elif options.mode == 'check':
        if options.noheadless:
            check_pages(options)
        else:
            virt_display(check_pages, options)


if __name__ == '__main__':
    main()
