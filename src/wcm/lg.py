import logging


class LgClass:
    def __init__(self):
        self._logger = logging.getLogger('.'.join([self.__class__.__module__, self.__class__.__name__]))
