# -*- coding: utf-8 -*-
# python <3
# 2013 Artur Skonecki

'''
A file containing classes implementing access to databases through SqlAlchemy
'''

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker, relationship, backref

Base = declarative_base()

class TExtract(Base):
  __tablename__ = 'extracts'

  id = Column(Integer, primary_key=True)

  url = Column(String(255), nullable=False)
  xpath = Column(String(255), nullable=False)
  contents = relationship("TContent", backref="extracts")

  def __init__(self, url=None, xpath=None, contents=None):
    self.url = url
    self.xpath = xpath
    for item in contents:
      self.contents.append( TContent( item ) )
  def __repr__(self):
    return "TExtract(%r, %r, %r)" % ( self.url, self.xpath, self.contents )

class TContent(Base):
  __tablename__ = 'contents'
  cid = Column(Integer, primary_key=True)
  parent_id = Column(Integer, ForeignKey('extracts.id'))
  content = Column(String(1023))

  def __init__(self, content=None):
    self.content = content

  def __repr__(self):
    return "TContent(%r)" % ( self.content )

class DbSupport( object ):

  def __init__( self, dba ):
    '''Contruct a new ``DbSupport`` object

    :param dba: specify database for SqlAlchemy
      e.g.:
        DbSupport( 'sqlite:///:memory:' )
    '''
    engine = create_engine( dba )
    Base.metadata.create_all( engine )

    Session = sessionmaker(bind=engine)
    self.session = Session()
    

  def write( self, url, xpath, extracts ):
    '''Write records to database'''
    try:
      for content in extracts.itervalues():
        print content
        self.session.add( TExtract( url, xpath, content ) )
      self.session.commit()
    except:
      self.session.rollback()
      raise

  def print_db( self ):
    '''Print out all TExtract records'''
    alldata = self.session.query(TExtract).all()
    for data in alldata:
      print( data )
