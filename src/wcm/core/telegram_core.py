from typing import List, Type

from telegram.ext import Updater, CommandHandler

from .base import BaseService
from .motion_tool import MotionTool
from .telegram_access import TelegramAccess
from .telegram_api.commands import ApiAclCmdCamPause, ApiAclCmdStart, ApiAclCmdCamStart, ApiAclCmdCamScr, \
    ApiAclCmdCamStatus, ApiAclCmdPrivateMod, ApiAclCmd, ApiAclCmdCam
from .telegram_api.subscriptions import ApiAclSbscrSendImg, ApiAclSbscrSendMsgAdm, ApiAclSbscrSendMsgAll


class TelegramCore(BaseService):

    def __init__(self, token: str, motion_tool: MotionTool, config: dict):
        super(TelegramCore, self).__init__()

        access_users = {}
        access_permits = {}
        if 'accesses' in config:
            accesses = config['accesses']
            if 'users' in accesses:
                access_users = accesses['users']
            if 'permits' in accesses:
                access_permits = accesses['permits']

        request_kwargs = {}
        if 'proxy' in config:
            request_kwargs['proxy_url'] = config['proxy']

        admin_acls = [ApiAclCmdCamPause, ApiAclSbscrSendMsgAdm, ApiAclCmdPrivateMod]
        user_acls = [ApiAclCmdCamStatus, ApiAclCmdCamStart, ApiAclCmdCamScr, ApiAclSbscrSendMsgAll,
                     ApiAclSbscrSendImg]
        all_acls = [ApiAclCmdStart]

        access = TelegramAccess(access_users, access_permits, admin_acls, user_acls, all_acls)
        upd = Updater(token=token, use_context=True, request_kwargs=request_kwargs)

        cb_send_msg_adm = ApiAclSbscrSendMsgAdm(access, upd, lambda x: None).callback
        cb_send_msg_all = ApiAclSbscrSendMsgAll(access, upd, cb_send_msg_adm).callback
        send_img = ApiAclSbscrSendImg(access, upd, cb_send_msg_adm)

        cmd_acls: List[Type[ApiAclCmd]] = []
        for acl in user_acls:
            if issubclass(acl, ApiAclCmd):
                if acl not in cmd_acls:
                    cmd_acls.append(acl)
        for acl in admin_acls:
            if issubclass(acl, ApiAclCmd):
                if acl not in cmd_acls:
                    cmd_acls.append(acl)
        for acl in all_acls:
            if issubclass(acl, ApiAclCmd):
                if acl not in cmd_acls:
                    cmd_acls.append(acl)

        for cmd in cmd_acls:
            if issubclass(cmd, ApiAclCmdCamScr):
                upd.dispatcher.add_handler(
                    CommandHandler(cmd.name, cmd(access, motion_tool, cb_send_msg_adm, send_img).do))
            elif issubclass(cmd, ApiAclCmdCam):
                upd.dispatcher.add_handler(CommandHandler(cmd.name, cmd(access, motion_tool, cb_send_msg_adm).do))
            else:
                upd.dispatcher.add_handler(CommandHandler(cmd.name, cmd(access, cb_send_msg_adm).do))

        self.__access = access
        self.__updater = upd

        self.send_msg_all = cb_send_msg_all
        self.send_msg_adm = cb_send_msg_adm
        self.send_img = send_img.callback

    def polling(self):
        # self._logger.debug(threading.get_ident())
        self.__updater.start_polling()

    def shutdown(self):
        self.__updater.stop()

    @property
    def running(self):
        return self.__updater.running

    @property
    def status(self):
        return {
            'access': self.__access.__dict__,
            'running': self.running
        }

    def private_mode_on(self, seconds):
        self.__access.set_private_mode(seconds)
        return True

    def private_mode_off(self):
        self.__access.set_norm_mode()
        return True
