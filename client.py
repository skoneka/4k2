#! /usr/bin/python2.7
# -*- coding: utf-8 -*-
# python <3
# 2013 Artur Skonecki

"""
An implementation of a client requesting extracts of contents of articles
in rss feed and fetching the response back over zmq sockets using json
as data format.
"""

import json
import zmq

from optparse import OptionParser

PORT = "5556"


# Connect to a server over zmq socket. Send a request for contents (xpath)
# from specific articles (article_nums) published on a rss feed (url). Fetch
# the reponse back.
def get_article_extracts( port, url, article_nums, xpath ):
  '''get_article_extracts( port, url, article_nums, xpath ) -> dict

  Return a dict containing rss article extracts.
  '''

  # connect to a server
  context = zmq.Context()
  socket = context.socket( zmq.REQ )
  socket.connect ( "tcp://localhost:%s" % port )

  # format and send a json request over zmq socket
  jdata = json.dumps( {
    "url":url,
    "article_nums": article_nums,
    "xpath": xpath
    } )
  print( "Sending request " + str( jdata ) )
  socket.send( jdata )

  # get the reply and decode json
  message = socket.recv()
  json_decoder = json.JSONDecoder()
  jdata_reply = json_decoder.decode( message )

  return jdata_reply

def main():
  '''main'''
  parser = OptionParser(
    usage = 'Usage: python client.py \
-f http://feeds.feedburner.com/TechCrunch \
-n 2,5,6,9,10 -s category' )

  parser.add_option( "-f", None,
    action="store",
    dest="url",
    default="http://feeds.feedburner.com/TechCrunch" )
  parser.add_option( "-n", None,
    action="store",
    dest="article_nums",
    default="1,2,3" )
  parser.add_option( "-s", None,
    action="store",
    dest="xpath",
    default = 'category' )

  options = parser.parse_args()[0]

  extracts = get_article_extracts( PORT,
    options.url,
    [ int( x ) for x in options.article_nums.split( ',' ) ],
    options.xpath )

  print( "Extracts " + str( extracts ) )

if __name__ == '__main__':
  main()


  

