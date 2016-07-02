#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Standard modules
import sys
import os
from os.path import isfile, getsize, expanduser, realpath
import argparse
import calendar, datetime, time
import sqlite3
import logging
import hashlib

# Extended modules

# Custom modules
from lib.schema import full_schema

def gen_logger(args):
    logger = logging.getLogger('activity_logger')
    lvl = logging.DEBUG if args.debug else logging.WARNING
    logger.setLevel(lvl)

    console_formatter = logging.StreamHandler('%(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if args.log:
        file_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        file_handler = logging.FileHandler(args.log_path)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

class StatusBar():

    """ StatusBar for loop events, not logged """

    def __init__(self, total, step_size, cons_width=64):
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) # For inline updates
        self.step_rate = min((step_size / total),1)
        self.adj_step = self.step_rate / cons_width   # Adjust step rate
        self.adj = self.adj_step            # Initialize adjusted step counter
        self.current = 0                    # Initialize current step
        print('[!]'),

    def step(self):
        self.current += 1

        if self.current >= self.adj:
            print('>'),
            self.adj += self.adj_step

    def done(self):
        print('[!]')

class DBGenerator():

    def __init__(self, args, schema):
        self.schema = schema
        self.args = args

    def generate(self):
        con = sqlite3.connect(Tracker.dbpath)

        with con:
            cur = con.cursor()
            cur.executescript(self.schema)

    def checksum(self):
        blk_size = 65536
        hasher = hashlib.sha256()

        with open(Tracker.dbpath, 'rb') as dbfile:
            buff = dbfile.read(blk_size)

            if self.args.debug:
                self.args.logger.debug('[*] Generating checksum')
                file_len = os.path.getsize(Tracker.dbpath)
                sb = StatusBar(file_len,blk_size)
                sb.step()

            while len(buff) > 0:
                hasher.update(buff)
                buff = dbfile.read(blk_size)
                if self.args.debug: sb.step()

        retval = hasher.hexdigest()

        if self.args.debug:
            sb.done()
            self.args.logger.debug('[*] sha256:{}..'.format(hasher.hexdigest()[:35]))

        return retval

class Tracker():

    # Primary tracker class
    dbpath = realpath('../data/activity.db')

    def __init__(self, args):
        self.dbcon = None
        self.args = args
        self.dbfile = Tracker.dbpath
        self.db = self._db_check()
        if not self.db:
            prompt = 'SQLite database not found, start a new tracker? : '
            if raw_input(prompt).upper()=='Y':
                self.db = self.gen_db()
            else:
                sys.exit(0)

    def _db_check(self):
        # Check for file existence and ensure the headers match sqlite3 length
        if not isfile(self.dbfile):
            return False

        return True

    def gen_db(self):
        dbgen = DBGenerator(self.args, full_schema)
        dbgen.generate()
        if self.args.debug: print dbgen.checksum()
        # Use checksum to ensure database has been created successfully
        # assert dbgen.checksum()==self.dbchksum, 'DBGenerator checksum mismatch'
        return True

    def main_loop(self):
        pass

    def load_activity(self, url):
        if 'http' not in url and '/' not in url:
            act_id = url
        else:
            act_id = url.split('/')[:-1]

        return Activity(self.dbquery(
                'SELECT * FROM activity WHERE id=?', (act_id)
                ))

    def get_notes(self, act_id):
        notes = self.dbquery('SELECT * FROM notes WHERE act_id=?',(act_id))

    def db_query(sql):
        with sqlite3.connect(self.dbfile) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(sql)
            return cur.fetchall()

class Activity():

    def __init__(self,row):
        self.url = url
        self.tag = tag
        self.label = url.split('/')[:-1]

    def add_description(self):
        print('Description :\n')
        self.description = multiline_input(True)

class Report():
    pass

def dbquery(sql,params=None,dictionary=False):
    with sqlite3.connect(self.dbfile) as con:

        if dictionary:
            con.row_factory = sqlite3.Row   # Uses a dictionary-based cursor
        cur = con.cursor()

        if params is None:
            cur.execute(sql)
        else:
            cur.execute(sql,params)

        return cur.fetchall()

def multiline_input(raw=False):
    # Be sure to print prompt before calling
    sentinel = ''
    func = raw_input if raw else input
    return '\n'.join(iter(func, sentinel))

def read_args():
    parser = argparse.ArgumentParser(
                        description = 'An activity tracker for ticket systems'
                        )
    parser.add_argument('action',
                        help='Specify an action',
                        choices=['add',
                                 'start',
                                 'stop',
                                 'done',
                                 'note',
                                 'delete',
                                 'status',
                                 'report'
                                 ],
                        type=str,
                        )
    parser.add_argument('item',
                        help='activity URL, ID, or report type',
                        type=str
                        )
    parser.add_argument('-d','--debug',
                        help='enable debug logging',
                        action='store_true'
                        )
    parser.add_argument('-l','--log',
                        help='save console/logging output to ~/activity.log',
                        action='store_true'
                        )
    parser.add_argument('-s','--status',
                        help='prints status of non-deleted activities',
                        action='store_true'
                        )
    return parser.parse_args()

# EVERYTHING below this line to be offloaded to the execution script

if __name__=='__main__':
    args = read_args()          #activity.read_args()
    args.log_path = expanduser('~/activity.log')
    args.logger = logger = gen_logger(args)       #activity.gen_logger()
    try:
        logger.debug("Generating tracker...")
        tracker = Tracker(args)
        logger.debug("Starting main_loop")
        tracker.main_loop()
    except KeyboardInterrupt:
        logger.debug('Keyboard Interrupt detected...')
        sys.exit(0)
    except SystemExit:
        logger.debug('Exit request detected')
        sys.exit(0)
    except IOError:
        if args.debug: raise
        logger.error('IOError encountered, disk?  perms?')
        sys.exit(10)
    except Exception as e:
        if args.debug: raise
        logger.error(e[0])
    else:
        logger.debug('Execution completed : {}'.format(
                datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                ))
