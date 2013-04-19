import zmq
import sys
import json
from optparse import OptionParser

port = "5556"


def main(url, feed_nums, xpath, ):
  context = zmq.Context()
  print "Connecting to server..."
  socket = context.socket(zmq.REQ)
  socket.connect ("tcp://localhost:%s" % port)
  
  #  Do 10 requests, waiting each time for a response
  for request in range (1,10):
    print "Sending request ", request,"..."
    jdata = json.dumps({
      "url":url,
      "feed_nums": feed_nums,
      "xpath": xpath
      })
    socket.send (jdata)
    #  Get the reply.
    message = socket.recv()
    print "Received reply ", request, "[", message, "]"

#end main


if __name__ == '__main__':
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

  

