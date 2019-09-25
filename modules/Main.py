#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Ovchinnikov Anatoly Vladimirovich
# Email: east@thyloved.ru
# Version: 1.0-2017

from PyQt5 import *  # подключает основные модули PyQt
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import *
import pytz
import sqlite3
import json
import sys

# Супер-класс

class Main(object):

    tz = False
    sqliteDb = 'local.db'
    sqliteConnection = False
    sqliteCursor = False
    timer = False
    serial = False
    allowed = ['00000000bbd1a2b4']

    def __init__(self):
        self.tz = pytz.timezone('Europe/Moscow')
        self.sqliteConnection = sqlite3.connect(self.sqliteDb)
        self.sqliteCursor = self.sqliteConnection.cursor()
        self.create_log_table()
        self.serial = self.getSerial()
        if self.serial not in self.allowed:
            sys.exit()

    def __del__(self):
        sqliteConnection.close()

    def getSerial(self):
        # Extract serial from cpuinfo file
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:6]=='Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"
        return cpuserial
    
    def create_log_table(self):
        self.sqliteCursor.execute("CREATE TABLE IF NOT EXISTS log_table (id INTEGER PRIMARY KEY AUTOINCREMENT, data VARCHAR, event VARCHAR, type VARCHAR, time TIMESTAMP DEFAULT (datetime('now','localtime')) )"
                                  )
        self.sqliteConnection.commit()

    def log(
        self,
        d,
        e,
        t,
        ):
        d = json.dumps(d)
        sql = 'INSERT INTO log_table (data, event, type) VALUES (?,?,?)'
        self.sqliteCursor.execute(sql, [d, e, t])
        self.sqliteConnection.commit()

    def readLog(
        self,
        l,
        o
        ):
        sql = 'SELECT * FROM log_table ORDER BY ID DESC LIMIT %s OFFSET %s;'%(l,o)
        d = self.sqliteCursor.execute(sql)
        d = d.fetchall()
        return d

    def vacuum(self):
        self.sqliteCursor.execute('VACUUM')
