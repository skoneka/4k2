import zmq
import time
import sys
import json
from mpi4py import MPI

port = "5556"

def main():
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

      print "Received json: ", jdata
      time.sleep (1)
      socket.send("World from %s" % port)
    else:
      jdata = None
    jdata = comm.bcast(jdata, root=0)
    print('job %d/%d data' %(rank, size))

  
if __name__ == '__main__':
  comm = MPI.COMM_WORLD
  size = comm.Get_size()
  rank = comm.Get_rank()
  main()
