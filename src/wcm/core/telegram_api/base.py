from typing import Callable

from telegram import Update

from wcm.core.telegram_access import TelegramAccess, TelegramAccessAcl
from wcm.lg import LgClass


class ApiAcl(LgClass, TelegramAccessAcl):

    def __init__(self, access: TelegramAccess, send_msg_adm: Callable[[str], None]):
        super(ApiAcl, self).__init__()
        self._access = access
        self.__send_msg_adm = send_msg_adm

    def _check_access(self, update: Update):
        chat_id = update.effective_chat.id
        user_name = update.effective_user.name
        if not self._access.check_user(chat_id, self, user_name):
            self._logger.error("Chat id %i want access to %s" % (chat_id, self.name))
            return False
        return True

    def _is_admin(self, update: Update):
        return self._access.is_admin(update.effective_chat.id)

    def _admin_log(self, update: Update, msg):
        if not self._is_admin(update):
            if self.__send_msg_adm is not None:
                self.__send_msg_adm("%s[%i][%i]: %s" % (
                    update.effective_user.name, update.effective_user.id, update.effective_chat.id, msg))
