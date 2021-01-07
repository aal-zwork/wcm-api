from ..lg import LgClass


class BaseService(LgClass):
    def __enter__(self):
        self.polling()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def polling(self):
        pass

    def shutdown(self):
        pass

    @property
    def running(self):
        return False

    @property
    def status(self):
        return self.__dict__
