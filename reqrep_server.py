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
    
    tree = etree.XML(xml)
    items = tree.xpath('channel/item')

    basic_range_width = len( items ) / size
    extended_range_width = len( items ) % size

    basic_slice = items[ rank * basic_range_width : ( rank + 1 ) * basic_range_width ]

    if rank == 0:
      basic_slice += items[ size * basic_range_width : size* basic_range_width + extended_range_width ]
      print( "e %d : %d %d / %d" % (rank, size * basic_range_width , size* basic_range_width + extended_range_width, len( items )))


    print( "%d : %d %d / %d" % (rank, rank * basic_range_width , ( rank + 1 ) * basic_range_width, len( items )))

    for item in basic_slice:
      print item
      print( item.xpath( jdata['xpath'] ) )

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
