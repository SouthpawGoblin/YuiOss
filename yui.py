# -*- coding: utf-8 -*-

from yui_oss import Yui, VERSION
import sys
import os

if __name__ == "__main__":
    path = sys.path[0]
    if os.path.isfile(path):
        path = os.path.dirname(path)
    yui = Yui(path + "/config.yaml")
    yui.run()


