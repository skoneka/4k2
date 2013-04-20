4k2 demonstrates concurrent XML xpath extraction. By Artur Skonecki.

Deployment
==========

Start server:
mpiexec -n 3 python server.py

Send requests with client:
python client.py \
-f http://feeds.feedburner.com/TechCrunch \
-n 2,5,6,9,10 -s category'

Hacking
=======

*server.py*
A program serving extracts of contents of articles in rss feed over zmq
sockets using json as data format.  This implementation uses MPI for
speeding up execution so it is taking advantage of concurrency features
of modern systems.

*client.py*
An implementation of a client:
- request from server extracts of contents of articles in rss feed
- fetch the response
- write results to a dummy database:
  TExtract( url, xpath, contents ) |one-to-many| TContent( content )
- print out database
Uses json as data format.
ZeroMQ is deployed for communication between client and server.
SQLAlchemy for database access.

*dbsupport.py*
A file containing classes implementing access to databases through SqlAlchemy.
