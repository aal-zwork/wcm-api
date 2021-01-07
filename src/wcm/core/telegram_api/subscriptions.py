import threading
from typing import Optional, IO

from telegram.ext import Updater

from .base import ApiAcl


class ErrorNotFoundApiAclSubscr(Exception):
    pass


class ApiAclSubscr(ApiAcl):
    def __init__(self, access, updater: Updater, send_msg_adm):
        super(ApiAclSubscr, self).__init__(access, send_msg_adm)
        self._updater = updater
        self._subscribe_lock = threading.Lock()
        self._subscritions = []

    def subscribe(self, chat_id):
        with self._subscribe_lock:
            # TODO need more beauty way
            if len(self._subscritions) > 10:
                self._logger.error("Subscribe more 10, clearing")
                self._subscritions.clear()
            self._subscritions.append(chat_id)

    def _unsubscribe(self) -> int:
        with self._subscribe_lock:
            if len(self._subscritions) > 0:
                return self._subscritions.pop(0)
        raise ErrorNotFoundApiAclSubscr()


class ApiAclSubscrSendMsg(ApiAclSubscr):
    def callback(self, msg: str) -> None:
        for chat in self._access.get_chats_by_acl(self):
            self._updater.dispatcher.bot.send_message(chat, msg, reply_markup=self._access.get_markup(chat))


class ApiAclSbscrSendMsgAdm(ApiAclSubscrSendMsg):
    name = 'send_msg_adm'


class ApiAclSbscrSendMsgAll(ApiAclSubscrSendMsg):
    name = 'send_msg_all'


class ApiAclSbscrSendImg(ApiAclSubscrSendMsg):
    name = 'send_img'

    def callback(self, image_buffer: Optional[IO[bytes]], msg: str or None = None):
        try:
            chat_id = self._unsubscribe()
        except ErrorNotFoundApiAclSubscr:
            for chat_id in self._access.get_chats_by_acl(self):
                markup = self._access.get_markup(chat_id)
                image_buffer.seek(0)
                self._updater.dispatcher.bot.send_photo(chat_id, image_buffer, reply_markup=markup)
                if msg is not None:
                    self._updater.dispatcher.bot.send_message(chat_id, msg, reply_markup=markup)
        else:
            markup = self._access.get_markup(chat_id)
            image_buffer.seek(0)
            self._updater.dispatcher.bot.send_photo(chat_id, image_buffer, reply_markup=markup)
            if msg is not None:
                self._updater.dispatcher.bot.send_message(chat_id, msg, reply_markup=markup)
            return
