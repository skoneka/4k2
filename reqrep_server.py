import zmq
import time
import sys
import json
from mpi4py import MPI
from lxml import etree
import urllib2



def main():
  port = "5556"
  if rank == 0:
    jsonDecoder = json.JSONDecoder()

    if len(sys.argv) > 1:
      port =  sys.argv[1]
      int(port)

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)

  while True:
    jdata = None
    xml = None
    if rank == 0:
      #  Wait for next request from client
      message = socket.recv()
      jdata = jsonDecoder.decode(message)
      xml = urllib2.urlopen(jdata['url']).read()


      #for i in range(1,size):
        #comm.send(jdata, dest = i, tag = 1 * i)
        #comm.send(xml, dest = i, tag = 11 * i)
        
      #comm.isend(jdata, dest = 2, tag = 2)
      #comm.isend(xml, dest = 2, tag = 22)
      #comm.isend(jdata, dest = 3, tag = 3)
      #comm.isend(xml, dest = 3, tag = 33)
      print "Received json: ", jdata
      #time.sleep (1)
      socket.send("World from %s" % port)

    jdata = comm.bcast(jdata, root=0)
    xml = comm.bcast(xml, root=0)
    
    feed_nums = jdata['feed_nums']
    xpath = jdata['xpath']
    
    tree = etree.XML(xml)
    items = tree.xpath('channel/item')

    basic_range_width = len( feed_nums ) / size
    extended_range_width = len( feed_nums ) % size

    slice_of_feed_nums = feed_nums[ rank * basic_range_width : ( rank + 1 ) * basic_range_width ]

    if rank == 0:
      slice_of_feed_nums += feed_nums[ size * basic_range_width : size* basic_range_width + extended_range_width ]
      #print( "e %d : %d %d / %d" % (rank, size * basic_range_width , size* basic_range_width + extended_range_width, len( feed_nums )))


    #print( "%d : %d %d / %d" % (rank, rank * basic_range_width , ( rank + 1 ) * basic_range_width, len( feed_nums )))


    rank_articles = {}
    
    for feed_num in slice_of_feed_nums:
      article_items = []
      #print items[ feed_num ].xpath( xpath )[0].text
      for item in items[ feed_num ].xpath( xpath ):
        article_items.append(item.text)
      #print( item.xpath( jdata['xpath'] ) )
      rank_articles[ feed_num ] = article_items

    print( 'rank ' + str( rank ) + ' articles ' + str( rank_articles ) )

    articles = comm.gather( rank_articles, root = 0 )

    if rank == 0:
      print( 'articles ' + str( articles ) )

      
    #print items
    jdata = None
    #jdata = comm.bcast(jdata, root=0)
    
    print('B job %d/%d data' %(rank, size))
    comm.Barrier()
    print('aB job %d/%d data' %(rank, size))

  
if __name__ == '__main__':

  comm = MPI.COMM_WORLD
  size = comm.Get_size()
  rank = comm.Get_rank()
  main()
