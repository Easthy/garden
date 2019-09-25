#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Ovchinnikov Anatoly Vladimirovich
# Email: east@thyloved.ru
# Version: 1.0-2017

import os
import json
import RPi.GPIO as GPIO
from pprint import pprint
import time
import datetime
import calendar
from Main import Main
import inspect
import traceback
import pdb
from PyQt5.QtCore import pyqtRemoveInputHook

class Garden(Main):

    settings_file = 'settings.json'
    settings = []
    io_translate = False  # {"on": 1, "off": 0}
    io_priority = False  # {"on": 2, "off": 1}
    schedules = []
    time_offset = 0
    pins = []  # Список пинов, используемых в работе. Использовать следующие: 11,12,13,15,16,18,22,29,31,32,33,35,36,37,38,40
    pins_functions = {
        GPIO.IN: 'IN',
        GPIO.OUT: 'OUT',
        GPIO.SPI: 'SPI',
        GPIO.I2C: 'I2C',
        GPIO.HARD_PWM: 'HARD_PWM',
        GPIO.SERIAL: 'SERIAL',
        GPIO.UNKNOWN: 'UNKOWN',
        }
    run = True

    def __init__(self, *args, **kwargs):
        super(Garden, self).__init__(*args, **kwargs)

    def __del__(self):
        self.log(None, 'Приложение закрыто', 'Событие')
        self.switchOffOut()
        GPIO.cleanup()

    def start(self):
        self.log(None, 'Запуск работы по расписанию', 'Событие')

        # Считать настройки из файла

        settings = self.readSettings(self.settings_file)
        self.setSettings(settings)
        self.initGPIO()
        self.setScheduler()
        self.run = True

    def stop(self):
        self.log(None, 'Остановка работы по расписанию', 'Событие')
        self.switchOffOut()
        self.run = False

    def switchOffOut(self):
        try:
            for (io, ch) in self.settings['GPIO']['channels'].items():
                if io == 'OUT':
                    self.setOut(ch, self.io_translate['off'])
        except:
            pass

    def initGPIO(self):
        self.log({'action': 'initGPIO', 'setting': self.settings},
                 'Установка настроек GPIO', 'Событие')

        # Установить нумерацию GPIO

        GPIO.setmode(getattr(GPIO, self.settings['GPIO']['mode']))

        # Установить режимы работы каналов

        for (io, ch) in self.settings['GPIO']['channels'].items():

            # ValueError: Channel must be an integer IF ch is list

            GPIO.setup(ch, getattr(GPIO, io))
            self.pins = self.pins + list(filter(lambda x: x \
                    not in self.pins, ch))

    def testSettings(self, settings_file):
        """Проверить правильность настроек"""

        return True

    def readSettings(self, settings_file):
        """Считать настройки из файла или взять дефолтные значения"""

        with open(settings_file) as file:
            data = json.load(file)
        return data

    def setSettings(self, settings):
        """Установить настройки"""

        if not settings:
            return False
        self.settings = settings
        self.io_translate = settings['GPIO']['out_values']
        self.io_priority = settings['GPIO']['out_priority']
        return True

    def setOut(self, ch, v):
        """Включить/выключить выхода"""

        if isinstance(ch, list):
            map(int, ch)
        else:
            ch = int(ch)
        self.log({'channel': ch, 'value': v}, 'Включение/отключение выходов', 'Событие')
        try:
            GPIO.output(ch, v)
        except ValueError:
            self.log({'channel': ch, 'value': v}, 'Включение/отключение выходов', 'Ошибка')

    def setGPIOScheduleDay(self):
        """Запланировать задание GPIO на 1 день согласно настройкам"""

        wd = str(datetime.datetime.now(self.tz).weekday())  # день недели
        day_schedule = False
        if wd in self.settings['schedule']:

            # задание на 1 день недели

            day_schedule = self.settings['schedule'][wd]
        if day_schedule is not False:
            for (action, ch_sched) in day_schedule.items():
                for (ch, t_sched) in ch_sched.items():
                    for t in t_sched:
                        h = int(t[0])
                        m = int(t[1])
                        now = datetime.datetime.now(self.tz)

                        # Время запуска с учётом временного сдвига

                        action_time = now.replace(hour=h, minute=m,
                                second=0) \
                            + datetime.timedelta(seconds=self.time_offset)
                        if action_time >= now:
                            action_time = self.DatetoUnix(action_time)
                            self.schedules.append({
                                'time': action_time,
                                'channel': ch,
                                'action': 'setOut',
                                'value': self.io_translate[action],
                                })
        self.log(day_schedule, 'Задано новое расписание', 'Событие')
        return day_schedule

    def setScheduler(self):
        """Запланировать задание GPIO на 1 день, следующее планирование через 1 день"""

        self.emptyScheduler()  # отменить все предыдущие задания
        self.log(None, 'Установка расписания', 'Событие')
        self.setGPIOScheduleDay()
        t = datetime.datetime.now(self.tz).date() \
            + datetime.timedelta(days=1, hours=0)
        t = self.DatetoUnix(t)
        self.schedules.append({'time': t, 'action': 'setScheduler'})

    def DatetoUnix(self, date):
        return time.mktime(date.timetuple())

    def listGPIOSchedule(self):
        """Получить запланированные задания GPIO"""

        return self.schedules

    def emptyScheduler(self):
        """Отменить ВСЕ запланированные задания"""

        self.log(None, 'Расписание удалено', 'Событие')
        self.schedules = []

    def watch(self):
        """Выполнить задания"""

        now = datetime.datetime.now(self.tz).replace(second=0,
                microsecond=0)
        now = self.DatetoUnix(now)
        execute = list(filter(lambda schedule: schedule['time'] == now,
                       self.schedules))
        self.schedules = [x for x in self.schedules if x not in execute]
        if execute:
            self.log({'action': 'watch', 'event': execute}, 'Выполнение задания по расписанию',
                     'Событие')
            for e in execute:
                if e['action'] == 'setOut':
                    self.setOut(e['channel'], e['value'])
                if e['action'] == 'setScheduler':
                    self.setScheduler()

    def invertOut(self):
        """Включить/отключить инверсию выходного сигнала"""

        on = 1
        off = 0
        result = False
        if self.settings['GPIO']['out_values']['on'] == 1:
            on = 0
            off = 1
            result = True
        self.settings['GPIO']['out_values']['on'] = on
        self.settings['GPIO']['out_values']['off'] = off
        self.log({'on': on, 'off': off}, 'Выходной сигнал инвертирован','Событие')
        pins = list( filter(lambda x: self.pins_functions[GPIO.gpio_function(x)] == 'OUT', self.pins) ) # Отфильтровать пины, к-е выполняют функции отличные от выхода (OUT)
        if len(pins) > 0:
            self.setOut(pins,off)
        return result

    def saveSettings(self):
        """Сохранить настройки в файл"""
        
        with open(self.settings_file, 'w') as outfile:
            json.dump(self.settings, outfile)
        self.setScheduler()

    def toggleOutput(self, ch):
        if self.pins_functions[GPIO.gpio_function(ch)] != 'OUT':
            return False
        else:
            self.setOut(ch, not GPIO.input(ch))
        return GPIO.input(ch)

    def readIOState(self, pins):
        states = {}
        for pin in pins:
            states['pin' + str(pin)] = \
                {'function': self.pins_functions[GPIO.gpio_function(pin)],
                 'value': GPIO.input(pin), 'pin': pin}
        return states

    def setTime(self, ts):
        try:
            d = datetime.datetime.strptime(ts, '%d.%m.%Y %H:%M')
            d = d.strftime('%m%d%H%M%Y')
            os.system('sudo date ' + d + '.01')
            self.log(ts, 'Изменено системное время', 'Событие')
        except ValueError:
            self.log(d, 'Ошибка установки времени', 'Ошибка')

    def cloneSchedule(
        self,
        cd,
        dd,
        o,
        ):
        if not dd:
            return self
        days = [dd]
        if dd == 'w':
            days = [
                '0',
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                ]
        for d in days:
            if d not in self.settings['schedule']:
                self.settings['schedule'][d] = {}
            if 'off' not in self.settings['schedule'][d]:
                self.settings['schedule'][d]['off'] = {}
            if 'on' not in self.settings['schedule'][d]:
                self.settings['schedule'][d]['on'] = {}
            self.settings['schedule'][d]['on'][o] = self.settings['schedule'][cd]['on'][o][:]
            self.settings['schedule'][d]['off'][o] = self.settings['schedule'][cd]['off'][o][:]
        return self

    def removeSchedule(
        self,
        d,
        o,
        t,
        a,
        ):
        try:
            t = t.split(':')
            index = self.settings['schedule'][d][a][o].index(t)
            self.settings['schedule'][d][a][o].pop(index)
            return self
        except ValueError:
            self.log([d, o, t, a], 'Удаление задания', 'Ошибка')

    def addSchedule(
        self,
        d,
        o,
        t,
        a,
        ):
        try:
            if d not in self.settings['schedule']:
                self.settings['schedule'][d] = {}
            if a not in self.settings['schedule'][d]:
                self.settings['schedule'][d][a] = {}
            if o not in self.settings['schedule'][d][a]:
                self.settings['schedule'][d][a][o] = []
            t = list(map(lambda i: i.zfill(2), t.split(':')))  # дополнить нулями до 2-х символов
            self.settings['schedule'][d][a][o].append(t)
            return self
        except ValueError:
            self.log([d, o, t, a], 'Добавление задания', 'Ошибка')
