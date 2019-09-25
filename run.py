#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Ovchinnikov Anatoly Vladimirovich
# Email: east@thyloved.ru
# Version: 1.0-2017

import os
import sys

# Подключить папку с модулями

sys.path.append(os.path.dirname(__file__) + 'modules')
from Garden import *
from PyQt5.QtWidgets import QApplication
from UiForm import *  # подключает модуль описания формы
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    g = Garden()
    app = QApplication(sys.argv)
    f = UiForm(g)
    f.web.show()
    f.draw('index')
    f.center()
    g.start()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
