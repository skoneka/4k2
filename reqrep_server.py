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
    if rank == 0:
      #  Wait for next request from client
      message = socket.recv()
      jdata = jsonDecoder.decode(message)
      xml = urllib2.urlopen(jdata['url']).read()

      for i in range(1,size):
        comm.send(jdata, dest = i, tag = 1 * i)
        comm.send(xml, dest = i, tag = 11 * i)
      #comm.isend(jdata, dest = 2, tag = 2)
      #comm.isend(xml, dest = 2, tag = 22)
      #comm.isend(jdata, dest = 3, tag = 3)
      #comm.isend(xml, dest = 3, tag = 33)
      print "Received json: ", jdata
      #time.sleep (1)
      socket.send("World from %s" % port)
    else:
      jdata = comm.recv(source = 0, tag = 1*rank)
      xml = comm.recv(source = 0, tag = 11*rank)
      tree = etree.XML(xml)
      items = tree.xpath('channel/item')
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
