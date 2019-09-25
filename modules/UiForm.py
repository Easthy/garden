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
from Garden import *


class WebView(QObject):

    ui_timer = False
    ui_up_freq = 500

    def __init__(self, parent=None):
        super(WebView, self).__init__(parent)


class UiForm(WebView):

    """Главная форма"""

    web = False
    page = False
    ui_path = \
        os.path.dirname(os.path.abspath(os.path.join(os.path.realpath(__file__),
                        os.pardir)))
    pages = {
        'index': QUrl.fromLocalFile(ui_path + '/ui/index.html'),
        'settings': QUrl.fromLocalFile(ui_path + '/ui/settings.html'),
        'manual': QUrl.fromLocalFile(ui_path + '/ui/manual.html'),
        'io-settings': QUrl.fromLocalFile(ui_path
                + '/ui/io-settings.html'),
        'time-settings': QUrl.fromLocalFile(ui_path
                + '/ui/time-settings.html'),
        'scheduler': QUrl.fromLocalFile(ui_path + '/ui/scheduler.html'
                ),
        'log': QUrl.fromLocalFile(ui_path + '/ui/log.html'
                ),
        }
    g = False
    current_page = False
    page_js = {
        'index': [{"f":'setMainButtonsEvents'}],
        'settings': [{'f': 'showInversion'}, {'f': 'showDate'}],
        'manual': [{'f': 'listPins'}, {'f': 'showIOState'}],
        'time-settings': [{'f': 'showDate'}, {'f': 'setCalendar'}],
        'scheduler': [{'f': 'scheduler'}],
        'log': [{'f': 'loadLog'}],
        }

    def __init__(self, g, parent=None):
        self.g = g
        super(UiForm, self).__init__(parent)

        # Обработка запланированных событий

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.g.watch)
        self.timer.start(1000)

        # Добавить объект страницы после загрузки страницы

        self.web = QWebView()
        self.web.resize(800, 480)
        self.page = self.web.page()
        self.web.loadFinished.connect(self.addWebView)
        self.web.loadFinished.connect(self.upWebView)

    def draw(self, page):

        self.web.load(self.pages[page])
        self.current_page = page

    def addWebView(self):
        """Добавить объект после загрузки страницы"""

        self.page.mainFrame().addToJavaScriptWindowObject('WebView',
                self)
        self.page.settings().setAttribute(QWebSettings.JavascriptEnabled,
                True)

    def upWebView(self):
        if self.current_page in self.page_js:
            for f in self.page_js[self.current_page]:
                getattr(self, f['f'])()

    def showInversion(self):
        btn_txt = 'Выключена'
        if self.g.settings['GPIO']['out_values']['on'] == 0:
            btn_txt = 'Включена'
        self.page.mainFrame().evaluateJavaScript("document.getElementById('inversion').innerHTML='"
                 + btn_txt + "'")

    def showDate(self):
        if self.current_page in ['settings', 'time-settings']:
            self.page.mainFrame().evaluateJavaScript('setDate();')
            self.jtimer = QtCore.QTimer()
            self.jtimer.singleShot(1000, self.showDate)

    def setCalendar(self):
        if self.current_page in ['time-settings']:
            self.page.mainFrame().evaluateJavaScript('setCalendar();')

    def showIOState(self):
        if self.current_page in ['manual']:
            states = self.g.readIOState(self.g.pins)
            self.page.mainFrame().evaluateJavaScript('\
	      var p = '
                     + json.dumps(states)
                    + ';\
	      for(var i in p){\
		  var cls_on = "btn-success";\
		  var cls_off = "btn-default";\
		  var add = cls_on;\
		  var remove = cls_off;\
		  if ( p[i]["value"] == 0 ){\
		      add = cls_off;\
		      remove = cls_on;\
		  }\
		  document.querySelector("a[data-io=\'"+p[i]["pin"]+"\']").classList.add(add);\
		  document.querySelector("a[data-io=\'"+p[i]["pin"]+"\']").classList.remove(remove);\
		  if ( p[i]["function"] != "OUT" ){\
		      document.querySelector("a[data-io=\'"+p[i]["pin"]+"\']").classList.add("disabled");\
		  }\
		  document.querySelector("a[data-io=\'"+p[i]["pin"]+"\'] .pin-func").innerHTML="(\"+p[i]["function"]+\")"\
	      }\
	    '
                    )
            self.jtimer = QtCore.QTimer()
            self.jtimer.singleShot(1000, self.showIOState)

    def showIOFunction(self):
        states = self.g.readIOState(self.g.pins)
        self.page.mainFrame().evaluateJavaScript('\
            var p = '
                 + json.dumps(states)
                + ';\
            for(var i in p){\
		document.querySelector("a[data-io=\'"+p[i]["pin"]+"\'] .pin-func").innerHTML="(\"+p[i]["function"]+\")"\
            }\
	'
                )

    def listPins(self):
        trs = ''
        for (k, pin) in enumerate(self.g.pins):
            if k % 4 == 0 and k != 0:
                trs += '</tr>'
            if k % 4 == 0:
                trs += '<tr>'
            trs += \
                '<td><a href="javascript:void(0)" class="btn btn-default" onclick="WebView.toggleOutput(' \
                + str(pin) + ')" data-io="' + str(pin) + '">#' \
                + str(pin) + ' <span class="pin-func"></span></a></td>'
        trs = '<tbody>' + trs + '</tbody>'
        self.page.mainFrame().evaluateJavaScript("document.getElementById('pins-list').innerHTML='"
                 + trs + "';")

    def scheduler(self):
        states = self.g.readIOState(self.g.pins)
        self.page.mainFrame().evaluateJavaScript('initSchedulerPage('
                + json.dumps(states) + ')')

    def loadLog(self):
        log = self.g.readLog(50,0)
        self.page.mainFrame().evaluateJavaScript('showLog('
                + json.dumps(log) + ')')

    def setMainButtonsEvents(self):
        log = self.g.readLog(50,0)
        r = 'true';
        if self.g.run == False:
            r = 'false'
        self.page.mainFrame().evaluateJavaScript('setMainButtonsEvents('+r+')')

    def center(self):

        # Центрирование окна приложения

        qr = self.web.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.web.move(qr.topLeft())

    @pyqtSlot()
    def start(self):
        self.g.start()

    @pyqtSlot()
    def stop(self):
        self.g.emptyScheduler()
        self.g.stop()

    @pyqtSlot(str)
    def openPage(self, trgt):
        self.draw(trgt)

    @pyqtSlot()
    def invertOut(self):
        self.g.invertOut()
        self.g.saveSettings()
        self.showInversion()

    @pyqtSlot(str)
    def toggleOutput(self, trgt):
        self.g.toggleOutput(int(trgt))
        self.showIOState()

    @pyqtSlot(str)
    def setTime(self, t):
        """Установка времени"""

        self.g.setTime(t)

    @pyqtSlot(str, str, str, str)
    def removeSchedule(
        self,
        d,
        o,
        ts,
        te,
        ):
        """Отмена одного цикла"""

        self.g.removeSchedule(d, o, ts, 'on').removeSchedule(d, o, te, 'off')
        self.g.saveSettings()
        self.loadSchedule(o, d)

    @pyqtSlot(str, str, str, str)
    def addSchedule(
        self,
        d,
        o,
        ts,
        te,
        ):
        """Добавление цикла"""

        self.g.addSchedule(d, o, ts, 'on').addSchedule(d, o, te, 'off').saveSettings()
        self.loadSchedule(o, d)

    @pyqtSlot(str, str)
    def loadSchedule(self, o, d):
        """Загрузка расписания на 1 день"""

        intervals = self.getIntervals(o, d)
        self.page.mainFrame().evaluateJavaScript('listIntervals('
                + json.dumps(intervals) + ',' + d + ');')

    @pyqtSlot(str, str, str)
    def cloneSchedule(
        self,
        cd,
        dd,
        o,
        ):
        """Копировать расписание на день/неделю"""
        self.g.cloneSchedule(cd, dd, o).saveSettings()

    def getIntervals(self, o, d):
        intervals = []
        s = {'on': [], 'off': []}  # schedules
        if d in self.g.settings['schedule']:  # day in schedule
            for a in s:  # action in schedule
                if o in self.g.settings['schedule'][d][a]:  # output in day action schedule
                    s[a] = self.g.settings['schedule'][d][a][o]
        if len(s['on']) > 0:
            s['on'].sort(key=lambda x: int(x[0] + x[1]))
        if len(s['off']) > 0:
            s['off'].sort(key=lambda x: int(x[0] + x[1]))
        for (i, v) in enumerate(s['on']):
            intervals.append(s['on'][i][0] + ':' + s['on'][i][1] + '-'
                             + s['off'][i][0] + ':' + s['off'][i][1])
        return intervals
