# -*- coding: utf-8 -*-
# Example usage: mpiexec -n 3 python server.py
# python <3
# 2013 Artur Skonecki

'''
A program serving extracts of contents of articles in rss feed over zmq
sockets using json as data format.  This implementation uses MPI for
speeding up execution so it is taking advantage of concurrency features
of modern systems.
'''

PORT = 5556

import json
import urllib2
import zmq

from lxml import etree
from mpi4py import MPI
import logging
import sys

import datetime

now = datetime.datetime.now()

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


sys.stderr = open("/tmp/stderr-4k2-server", 'w')
sys.stdout = open("/tmp/stdout-4k2-client", 'w')
sys.stderr.write("hello-" + now.strftime("%Y-%m-%d %H:%M") + "\n")

sys.stdout.flush(); sys.stderr.flush()

class InvalidCredentialsError(Exception):
    '''thrown on Invalid authentication tokens''' 
    pass

def is_authenticated(appid, apikey):
    '''a placeholder for proper accessing a database of registered api users'''
    print appid, apikey
    if appid == "myawesomeapp" and apikey == "mysecretapikey":
        print True
        return True
    else:
        print False
        return False


def extract( xml, article_nums, xpath ):
  '''extract( xml, article_nums, xpath ) -> dict

  Return a dict containing article extracts.
  '''

  # extract items containing articles
  tree = etree.XML( xml )
  items = tree.xpath( 'channel/item' )

  # divide articles between RANKs for processing
  basic_range_width = len( article_nums ) / SIZE
  extended_range_width = len( article_nums ) % SIZE

  slice_of_article_nums = article_nums[
    RANK * basic_range_width : ( RANK + 1 ) * basic_range_width ]

  # assign the remainder of articles to RANK 0
  if RANK == 0:
    slice_of_article_nums += article_nums[
      SIZE * basic_range_width :
      SIZE * basic_range_width + extended_range_width ]

  # contains extracts from articles for a given xpath in a RANK
  # e.g. RANK 0 articles {1: ['Gadgets'], 4: ['TC'], 5: ['Mobile']}
  rank_article_extracts = {}

  for article_num in slice_of_article_nums:
    article_extracts = []
    # extract contents from every artile based on xpath
    try:
      for item in items[ article_num ].xpath( xpath ):
        article_extracts.append(item.text)
    except etree.XPathEvalError:
      logging.error('Invalid xpath')
      pass
    rank_article_extracts[ article_num ] = article_extracts

  ## print out extracts of articles for the current RANK
  #print( 'RANK ' + str( RANK ) +
  #  ' articles ' + str( rank_article_extracts ) )

  # get all extracts form RANKs
  extracts = COMM.gather( rank_article_extracts, root = 0 )

  # join returned dicts in extracts into a single dict
  if RANK == 0:
    nextracts = {}
    for data in extracts:
      nextracts.update(data)
  else:
    nextracts = None

  return nextracts


def server( port ):
  '''server( port )

  Start a server listening for connections with zmq socket at 'port'
  for json requests from clients.

  Request fromat:
  {
  "url":url,
  "article_nums": article_nums,
  "xpath": xpath
  }

  Reply format:
  {
  "article number' : list of extracted items,
  ...
  }
  '''
  sys.stderr.write("hello RANK %d\n" % RANK)
  sys.stdout.flush(); sys.stderr.flush()
  if RANK == 0:
    json_decoder = json.JSONDecoder()

    # set up a socket for communication with clients
    context = zmq.Context()
    socket = context.socket( zmq.REP )
    socket.bind( "tcp://*:%s" % port )
    sys.stderr.write("server starting at %s\n" % port)
    sys.stdout.flush(); sys.stderr.flush()

  while True:
    try:
        jdata = None
        xml = None
        if RANK == 0:
          #  Wait for a next json request from clients and decode json
          message = socket.recv()
          jdata = json_decoder.decode( message )
          if not is_authenticated( jdata['APPID'], jdata['APIKEY']):
              raise InvalidCredentialsError
          xml = urllib2.urlopen( jdata['url'] ).read()
          logging.info( "Received json: " + str( jdata ) )
    
        # send data to other RANKs
        jdata = COMM.bcast( jdata, root=0 )
        xml = COMM.bcast( xml, root=0 )
        sys.stderr.write("bcast RANK %d\n" % RANK)
        sys.stdout.flush(); sys.stderr.flush()
    
        article_nums = jdata[ 'article_nums' ]
        xpath = jdata[ 'xpath' ]
    
        # do the magic - extract contents from articles based on xpath
        extracts = extract( xml, article_nums, xpath )
    
        # send extracts of articles down the pipe
        if RANK == 0:
          logging.info( 'Sending extracts ' + str( extracts ) )
          jdata = json.dumps( extracts )
          socket.send( jdata )
    except InvalidCredentialsError:
        logging.warning("Invalid credentials")



if __name__ == '__main__':

  # initialize MPI
  COMM = MPI.COMM_WORLD
  SIZE = COMM.Get_size()
  RANK = COMM.Get_rank()

  server( PORT )


