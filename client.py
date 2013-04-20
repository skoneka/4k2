import json
import os
import sys
import zmq
# -*- coding: utf-8 -*-
# python <3
# 2013 Artur Skonecki

from optparse import OptionParser

port = "5556"

def main(url, article_nums, xpath, ):

  print( "Connecting to server..." )
  context = zmq.Context()
  socket = context.socket( zmq.REQ )
  socket.connect ( "tcp://localhost:%s" % port )
  
  jdata = json.dumps( {
    "url":url,
    "article_nums": article_nums,
    "xpath": xpath
    } )
  print( "Sending request " + str( jdata ) )
  socket.send( jdata )
  
  #  Get the reply.
  message = socket.recv()
  jsonDecoder = json.JSONDecoder()
  jdata_reply = jsonDecoder.decode( message )
  print( "Received reply " + str( jdata_reply ) )

if __name__ == '__main__':
  parser = OptionParser( usage = '''Usage: python client.py -f http://feeds.feedburner.com/TechCrunch -n 2,5,6,9,10 -s /
  html/body/div/div[1]/ul/li[3]''' )

  parser.add_option( "-f", None,
    action="store",
    dest="url",
    default="http://feeds.feedburner.com/TechCrunch" )
  parser.add_option( "-n", None,
    action="store",
    dest="article_nums",
    default="1,2" )
  parser.add_option( "-s", None,
    action="store",
    dest="xpath",
    default = '/html/body/div[1]/ul/li' )

  (options, args) = parser.parse_args()
  print( options )

  main( options.url,
    map( int, options.article_nums.split( ',' ) ),
    options.xpath )

  

