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


class Page(object):

    def __init__(self, url, xpath):
        self.url = url
        self.xpath = xpath
        self.match = None
        self.filename = None

    def save(self):
        if self.filename is None:
            # create alphanumeric filename from URL
            self.filename = re.sub('(^https?://|[\W_]+)', '', self.url)
        filename = os.path.join(os.path.expanduser('~'), '.pagechange', self.filename)
        print filename
        with open(filename, 'wb') as picklefile:
            pickle.dump(self, picklefile)

            
class PageChange(object):

    def __init__(self):
        #self.driver = webdriver.Firefox()
        self.driver = webdriver.Chrome()
        self.waittime = 5

    def check(self, page):
        self.driver.get(page.url)
        self.driver.implicitly_wait(self.waittime)
        # assert "Python" in driver.title
        xpmatch = self.driver.find_element(By.XPATH, page.xpath)
        return xpmatch.text

def get_options():
    parser = OptionParser()
    parser.add_option("-u", help="url", dest="url")
    parser.add_option("-x", help="xpath", dest="xpath")
    (options, args) = parser.parse_args()
    return (options, args)

def main():
    (options, args) = get_options()
    if None in (options.url, options.xpath):
        print "No url/xpath provided"
    else:
        try:
            p = Page(options.url, options.xpath)
            pc = PageChange()
            res = pc.check(p)
        except:
            pass
        p.match = res
        p.save()
        print res
        pc.driver.close()

if __name__ == '__main__':
    main()
    
