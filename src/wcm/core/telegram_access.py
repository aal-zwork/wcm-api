import threading
from typing import Dict, List, Type

from telegram import KeyboardButton, ReplyKeyboardMarkup

from wcm.lg import LgClass

MODE_NORM = 0
MODE_PRIVATE = 1

PERMIT_UNKNOWN = -1
PERMIT_ALL = 0
PERMIT_ADMIN = 1
PERMIT_USER = 2
PERMIT_YAML_NAMES = ['ALL', 'ADMIN', 'USER']


class TelegramAccessAcl:
    name = None
    ismarkup = False


class TelegramAccess(LgClass):
    def __init__(self, users: dict, permits: dict,
                 admin_acls: List[Type[TelegramAccessAcl]],
                 user_acls: List[Type[TelegramAccessAcl]],
                 all_acls: List[Type[TelegramAccessAcl]]):
        super(TelegramAccess, self).__init__()
        self.__user_to_chat_id: Dict[str, int] = {}
        self.__permit_to_users: Dict[int, List[str]] = {
            PERMIT_UNKNOWN: [],
            PERMIT_ADMIN: [],
            PERMIT_USER: [],
            PERMIT_ALL: []
        }
        self.__permit_to_acls: Dict[int, List[Type[TelegramAccessAcl]]] = {
            PERMIT_UNKNOWN: [],
            PERMIT_ADMIN: admin_acls,
            PERMIT_USER: user_acls,
            PERMIT_ALL: all_acls
        }
        self.__user_to_markup: Dict[str, ReplyKeyboardMarkup] = {}
        self.__mode = MODE_NORM
        self.__mode_lock = threading.Lock()
        self.__mode_timer: threading.Timer or None = None

        for acl in user_acls:
            if acl not in self.__permit_to_acls[PERMIT_ADMIN]:
                self.__permit_to_acls[PERMIT_ADMIN].append(acl)

        for user_name, user_id in users.items():
            self.__user_to_chat_id[user_name] = user_id

        for permit_name, user_names in permits.items():
            for user_name in user_names:
                self.__permit_to_users[PERMIT_YAML_NAMES.index(permit_name)].append(user_name)

        for user in self.__user_to_chat_id:
            self.__generate_user_markup(user)

    def get_chats_by_acl(self, acl: TelegramAccessAcl) -> List[int]:
        chats = []
        acl_type = type(acl)
        for permit, acls in self.__permit_to_acls.items():
            if permit in self.__permit_to_users and acl_type in acls:
                for user in self.__permit_to_users[permit]:
                    if self.__mode == MODE_PRIVATE and \
                            user not in self.__permit_to_users[PERMIT_ADMIN]:
                        continue
                    chat = self.__user_to_chat_id[user]
                    if chat not in chats:
                        chats.append(chat)
        return chats

    def get_markup(self, chat_id) -> ReplyKeyboardMarkup or None:
        for user, user_chat_id in self.__user_to_chat_id.items():
            if chat_id == user_chat_id:
                if user in self.__user_to_markup:
                    return self.__user_to_markup[user]
        return None

    def check_user(self, chat_id, acl: TelegramAccessAcl, user_name=None) -> bool:
        acl_type = type(acl)
        if acl_type in self.__permit_to_acls[PERMIT_ALL]:
            if chat_id not in self.__user_to_chat_id.values():
                if user_name is not None:
                    self.__user_to_chat_id[user_name] = chat_id
                    self.__generate_user_markup(user_name)
                else:
                    self.__user_to_chat_id[str(chat_id)] = chat_id
                    self.__generate_user_markup(str(chat_id))
            return True
        return chat_id in self.get_chats_by_acl(acl)

    def is_admin(self, chat_id) -> bool:
        for adm in self.__permit_to_users[PERMIT_ADMIN]:
            if chat_id == self.__user_to_chat_id[adm]:
                return True
        return False

    def set_norm_mode(self) -> None:
        with self.__mode_lock:
            self.__mode = MODE_NORM
            if isinstance(self.__mode_timer, threading.Timer):
                self.__mode_timer.cancel()
                self.__mode_timer = None

    def set_private_mode(self, seconds: float) -> None:
        with self.__mode_lock:
            self.__mode = MODE_PRIVATE
            if self.__mode_timer is None:
                self.__mode_timer = threading.Timer(seconds, self.__timer_work)
                self.__mode_timer.start()

    @property
    def mode(self) -> str:
        if self.__mode == MODE_NORM:
            return "Нормальный"
        if self.__mode == MODE_PRIVATE:
            return "Приватный"
        return "Неизвестный"

    @property
    def is_norm_mode(self) -> bool:
        return self.__mode == MODE_NORM

    @property
    def is_private_mode(self) -> bool:
        return self.__mode == MODE_PRIVATE

    def __generate_user_markup(self, user) -> None:
        buttons = []
        buttons_line = []
        for permit, users in self.__permit_to_users.items():
            if user in users:
                for acl in self.__permit_to_acls[permit]:
                    if acl.name is not None and acl.ismarkup:
                        buttons_line.append(KeyboardButton("/%s" % acl.name))
                        if len(buttons_line) > 2:
                            buttons.append(buttons_line)
                            buttons_line = []
        buttons.append(buttons_line)
        self.__user_to_markup[user] = ReplyKeyboardMarkup(buttons)

    def __timer_work(self):
        self.set_norm_mode()
