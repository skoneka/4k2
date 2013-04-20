# -*- coding: utf-8 -*-
# python <3
# 2013 Artur Skonecki

import json
import sys
import time
import urllib2
import zmq

from lxml import etree
from mpi4py import MPI

port = 5556

def main( port ):
  if rank == 0:
    jsonDecoder = json.JSONDecoder()

    # set up a socket for communication with clients
    context = zmq.Context()
    socket = context.socket( zmq.REP )
    socket.bind( "tcp://*:%s" % port )

  while True:
    jdata = None
    xml = None
    if rank == 0:
      #  Wait for next json request from client
      message = socket.recv()
      jdata = jsonDecoder.decode( message )
      xml = urllib2.urlopen( jdata['url'] ).read()
      print( "Received json: " + str( jdata ) )

    # send data to other ranks
    jdata = comm.bcast( jdata, root=0 )
    xml = comm.bcast( xml, root=0 )

    article_nums = jdata[ 'article_nums' ]
    xpath = jdata[ 'xpath' ]

    # extracts items containing articles
    tree = etree.XML( xml )
    items = tree.xpath( 'channel/item' )

    # divide articles between ranks for processing
    basic_range_width = len( article_nums ) / size
    extended_range_width = len( article_nums ) % size

    slice_of_article_nums = article_nums[ rank * basic_range_width : ( rank + 1 ) * basic_range_width ]

    # assign the remainder of articles to rank 0
    if rank == 0:
      slice_of_article_nums += article_nums[ size * basic_range_width : size* basic_range_width + extended_range_width ]

    # contains extracts from articles for a given xpath in a rank
    # e.g. rank 0 articles {1: ['Gadgets'], 4: ['TC'], 5: ['Mobile']}
    rank_article_extracts = {}

    for article_num in slice_of_article_nums:
      article_extracts = []
      # extract contents from every artile based on xpath
      for item in items[ article_num ].xpath( xpath ):
        article_extracts.append(item.text)
      rank_article_extracts[ article_num ] = article_extracts

    ## print out extracts of articles for the current rank
    #print( 'rank ' + str( rank ) + ' articles ' + str( rank_article_extracts ) )

    # get all extracts form ranks 
    extracts = comm.gather( rank_article_extracts, root = 0 )

    # send extracts of articles down the pipe
    if rank == 0:
      print( 'Sending extracts ' + str( extracts ) )
      jdata = json.dumps( extracts )
      socket.send( jdata )


if __name__ == '__main__':
  if len( sys.argv ) > 1:
    port =  int( sys.argv[1] )

  # initialize MPI
  comm = MPI.COMM_WORLD
  size = comm.Get_size()
  rank = comm.Get_rank()
  
  main( port )
