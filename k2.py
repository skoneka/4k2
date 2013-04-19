# -*- coding: utf-8 -*-
# python <3
# 2013 Artur Skonecki
import urllib2
from lxml import etree
import multiprocessing
import sys

_html = ''
_xpath=''
tree = None

def get_el(data):
  global _html, _xpath, tree
  tree = etree.XML(_html)
  els = tree.xpath(_xpath)
  feed_num = data
  try:
    print(els[feed_num])
    return els[feed_num]
  except IndexError:
    sys.stderr.write('No such element %d\n' % data);
    return None

  
def main(url, feed_nums, xpath, ):
  global _html, _xpath
  _html = urllib2.urlopen(url).read()
  _xpath = xpath

  #pool_size = multiprocessing.cpu_count() * 2
  #pool = multiprocessing.Pool(processes=pool_size)

  #o = pool.map(get_el, feed_nums)

  tree = etree.XML(_html)
  items = tree.xpath('channel/item')
  els = tree.xpath(_xpath)
  feed_num = data
  try:
    print(els[feed_num])
    return els[feed_num]
  except IndexError:
    sys.stderr.write('No such element %d\n' % data);
    return None

  
  
  print o
  return o
  


if __name__ == '__main__':
  from optparse import OptionParser
  
  parser = OptionParser(usage = '''Usage: python program.py -f http://feeds.feedburner.com/TechCrunch -n 2,5,6 -s /
  html/body/div/div[1]/ul/li[3]''')

  parser.add_option("-f", None,
    action="store", # optional because action defaults to "store"
    dest="url",
    default="file:///home/lab/k2/test.html")
  parser.add_option("-n", None,
    action="store", # optional because action defaults to "store"
    dest="feed_nums",
    default="1,2",)
  parser.add_option("-s", None,
    action="store", # optional because action defaults to "store"
    dest="xpath",
    default = '/html/body/div[1]/ul/li')
  
  (options, args) = parser.parse_args()
  print options

  o = main( options.url,
    map(int, options.feed_nums.split(',')),
    options.xpath )
  

  