#!/usr/bin/env python3
import logging

from wcm.core import WcmCore

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s[%(name)s][%(levelname)s][%(funcName)s:%(lineno)s]: %(message)s',
                        level=logging.INFO)
    wcm = WcmCore()
    wcm.polling()
