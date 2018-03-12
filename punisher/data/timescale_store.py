import os
import json
import datetime
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.functions import database_exists, create_database
from sqlalchemy import Integer, String, DateTime, Float, JSON, Boolean, BigInteger
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Table
from sqlalchemy import select, update
from sqlalchemy import or_
from sqlalchemy import and_
from sqlalchemy import between

import punisher.config as cfg
import punisher.constants as c
from punisher.utils import files
from punisher.utils.dates import str_to_date, date_to_str
from punisher.utils.dates import epoch_to_utc, utc_to_epoch
from punisher.utils.encoders import EnumEncoder

from .store import DataStore

"""
http://rickyhan.com/jekyll/update/2017/10/27/how-to-handle-order-book-data.html
https://www.pythonsheets.com/notes/python-sqlalchemy.html
http://sqlalchemy-utils.readthedocs.org/en/latest/database_helpers.html
https://www.postgresql.org/docs/devel/static/auth-pg-hba-conf.html
"""

DEFAULT_START = utc_to_epoch(datetime.datetime(year=1970, month=1, day=1))*1000
DB_ISOLATION_LEVEL = 'READ COMMITTED'
DB_POOL_RECYCLE = 3600

def get_engine():
    postgres_db = {
        'drivername': cfg.TIMESCALE_DB_DRIVER,
        'username': cfg.TIMESCALE_DB_USERNAME,
        'password': cfg.TIMESCALE_DB_PASSWORD,
        'host': cfg.TIMESCALE_DB_HOSTNAME,
        'database': cfg.TIMESCALE_DB_NAME,
        'port': cfg.TIMESCALE_DB_PORT
    }
    db_uri = URL(**postgres_db)
    return create_engine(
        db_uri,
        convert_unicode=True,
        isolation_level=DB_ISOLATION_LEVEL,
        pool_recycle=DB_POOL_RECYCLE,
        pool_size=1
    )


def setup_db(engine):
    if not database_exists(engine.url):
        create_database(engine.url)
    db = scoped_session(sessionmaker(autocommit=False,
    								 autoflush=False,
    								 bind=engine))
    base = declarative_base()
    base.query = db.query_property()
    return base

# Global Pool
if cfg.TIMESCALE_DB_ENABLED:
    engine = get_engine()
    base = setup_db(engine)

def get_session():
    return scoped_session(
        sessionmaker(autocommit=False,
        autoflush=False,
        bind=engine))

def get_conn():
    return engine.connect()

def get_meta():
    meta = MetaData(engine)
    meta.reflect()
    return meta

def get_tables():
    return get_meta().tables

def get_table_name(prefix, ex_id, asset):
    return '{}_{}_{}'.format(prefix, ex_id, asset.symbol).lower()

def get_trades_table(ex_id, asset):
    meta = get_meta()
    name = get_table_name('trades', ex_id, asset)
    if name in meta.tables:
        table = Table(name, meta)
    else:
        table = Table(name, meta,
            Column('seq', BigInteger, primary_key=True),
            Column('ts', BigInteger, nullable=False), #ms
            Column('is_trade', Boolean, nullable=False),
            Column('is_bid', Boolean, nullable=False),
            Column('price', Float, nullable=False),
            Column('quantity', Float, nullable=False),
        )
        table.create(engine)
    return table

def get_trade(table, conn, seq):
    query = select([table]).where(table.c.seq == seq)
    row = conn.execute(query).first()
    if row is not None:
        return Trade.from_tuple(row)
    return None

def get_trades(table, start=None, end=None):
    end = end if end is not None else utc_to_epoch(datetime.datetime.utcnow())*1000
    start = start if start is not None else DEFAULT_START
    conn = get_conn()
    query = select([table]).where(
        between(table.c.ts, start, end))
    try:
        res = conn.execute(query).fetchall()
        return res
    except SQLAlchemyError as e:
        print (e)
    finally:
        conn.close()

def insert_or_update_trades(table, trades):
    conn = get_conn()
    try:
        for t in trades:
            insert_or_update_trade(
                table, conn, t['seq'], t['ts'], t['is_trade'],
                t['is_bid'], t['price'], t['quantity']
            )
    except SQLAlchemyError as e:
        print (e)
    finally:
        conn.close()

def insert_or_update_trade(table, conn, seq, ts, is_trade,
                           is_bid, price, quantity):
    if get_trade(table, conn, seq) is None:
        insert_trade(
            table, conn, seq, ts, is_trade, is_bid, price, quantity
        )
    else:
        update_trade(
            table, conn, seq, ts, is_trade, is_bid, price, quantity
        )

def update_trade(table, conn, seq, ts, is_trade, is_bid, price, quantity):
    query = update(table).where(
        table.c.seq==seq).values({
            'ts':ts,
            'is_trade':is_trade,
            'is_bid':is_bid,
            'price':price,
            'quantity':quantity})
    conn.execute(query)

def insert_trade(table, conn, seq, ts, is_trade, is_bid, price, quantity):
    ins = table.insert().values(
        seq=seq,
        ts=ts,
        is_trade=is_trade,
        is_bid=is_bid,
        price=price,
        quantity=quantity
    )
    conn.execute(ins)

def bulk_insert(table, rows):
    """
    [
       {'l_name':'Hi','f_name':'bob'},
       {'l_name':'yo','f_name':'alice'}
    ]
    """
    conn = get_conn()
    try:
        conn.execute(table.insert(), rows)
    except SQLAlchemyError as e:
        print (e)
    finally:
        conn.close()


class Trade():
    def __init__(self, seq, ts, is_trade, is_bid, price, quantity):
        self.seq = seq
        self.ts = ts
        self.is_trade = is_trade
        self.is_bid = is_bid
        self.price = price
        self.quantity = quantity

    @classmethod
    def from_tuple(self, tup):
        return Trade(
            seq=tup[0],
            ts=tup[1],
            is_trade=tup[2],
            is_bid=tup[3],
            price=tup[4],
            quantity=tup[5],
        )

    @classmethod
    def from_dct(self, dct):
        return Trade(
            seq=dct['seq'],
            ts=dct['ts'],
            is_trade=dct['is_trade'],
            is_bid=dct['is_bid'],
            price=dct['price'],
            quantity=dct['quantity'],
        )

    def to_dct(self):
        return {
            'seq': self.seq,
            'ts': self.utc,
            'is_trade': self.is_trade,
            'is_bid': self.is_bid,
            'price': self.price,
            'quantity': self.quantity,
        }

    @property
    def utc(self):
        return epoch_to_utc(self.ts // 1000)

    def __repr__(self):
        return "Trade: {} Utc: {} isTrade: {} isBid: {} Price: {} Qty: {}".format(
            self.seq, date_to_str(self.utc), self.is_trade, self.is_bid,
            self.price, self.quantity
        )
