from telegram import Update
from telegram.ext import CallbackContext

from wcm.core.motion_tool import MotionTool
from .base import ApiAcl
from .subscriptions import ApiAclSubscr


class ApiAclCmd(ApiAcl):
    ismarkup = True

    def do(self, update: Update, context: CallbackContext):
        pass


class ApiAclCmdStart(ApiAclCmd):
    name = 'start'
    ismarkup = False

    def do(self, update: Update, context: CallbackContext):
        if not self._check_access(update):
            return
        user = update.effective_user
        chat_id = update.effective_chat.id
        msg = 'Hi, your id: %i, chat id: %i' % (user.id, chat_id)
        self._admin_log(update, "wants to something from us(%i)" % chat_id)
        context.bot.send_message(chat_id=chat_id, text=msg,
                                 reply_markup=self._access.get_markup(chat_id))


class ApiAclCmdCam(ApiAclCmd):
    def __init__(self, access, motion_tool: MotionTool, cb_admin_log):
        super(ApiAclCmdCam, self).__init__(access, cb_admin_log)
        self._motion_tool = motion_tool

    def _premake_cams(self, args):
        cams = []
        msg = ""
        if len(args) > 0:
            wcm_cam_id = int(args[0])
            try:
                cam = self._motion_tool.find_cam_by_wcm_cam_id(wcm_cam_id)
            except Exception as e:
                msg += 'Камера не найдена: %i' % wcm_cam_id
                msg += '\n'
                self._logger.error("Cam not found %i (%s)" % (wcm_cam_id, str(e)))
            else:
                cams.append(cam)
        else:
            cams = self._motion_tool.cams
        return [cams, msg]


class ApiAclCmdCamStatus(ApiAclCmdCam):
    name = 'cam_status'

    def do(self, update: Update, context: CallbackContext):
        if not self._check_access(update):
            return
        statuses = self._motion_tool.cams.status
        state_msg = ""
        if self._is_admin(update):
            state_msg = "Статус системы: %s\n" % self._access.mode
        cam_msg = ''
        for cam_name, status in statuses.items():
            cam_msg += "%s: %s\n" % (cam_name, status)
        if cam_msg == "":
            cam_msg = "Камеры отсутсвуют"
        msg = state_msg + cam_msg
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg,
                                 reply_markup=self._access.get_markup(update.effective_chat.id))


class ApiAclCmdCamStart(ApiAclCmdCam):
    name = 'cam_start'

    def do(self, update: Update, context: CallbackContext):
        if not self._check_access(update):
            return
        [cams, msg] = self._premake_cams(context.args)
        for cam in cams:
            try:
                cam.start()
            except Exception as e:
                msg += 'Проблема с камерой %s' % cam.print_name
                msg += '\n'
                self._logger.error("Problem with a camera %s (%s)" % (cam.print_name, str(e)))
            else:
                msg = '%s запуск...' % cam.print_name
                msg += '\n'
        if msg == "":
            msg = "Камер для запуска нет"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg,
                                 reply_markup=self._access.get_markup(update.effective_chat.id))
        self._admin_log(update, msg)


class ApiAclCmdCamPause(ApiAclCmdCam):
    name = 'cam_pause'

    def do(self, update: Update, context: CallbackContext):
        if not self._check_access(update):
            return
        [cams, msg] = self._premake_cams(context.args)
        for cam in cams:
            try:
                cam.pause()
            except Exception as e:
                msg += 'Проблема с камерой %s' % cam.print_name
                msg += '\n'
                self._logger.error("Problem with a camera %s (%s)" % (cam.print_name, str(e)))
            else:
                msg = '%s остановка...' % cam.print_name
                msg += '\n'
        if msg == "":
            msg = "Камер для остановки нет"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg,
                                 reply_markup=self._access.get_markup(update.effective_chat.id))
        self._admin_log(update, msg)


class ApiAclCmdCamScr(ApiAclCmdCam):
    name = 'cam_scr'

    def __init__(self, access, motion_tool: MotionTool, cb_admin_log, subscription: ApiAclSubscr):
        super(ApiAclCmdCam, self).__init__(access, cb_admin_log)
        self._motion_tool = motion_tool
        self.subscription = subscription

    def do(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        if not self._check_access(update):
            return
        [cams, msg] = self._premake_cams(context.args)
        for cam in cams:
            try:
                if not isinstance(self._motion_tool, MotionTool):
                    raise Exception
                cam.screenshot()
                self.subscription.subscribe(chat_id)
            except Exception as e:
                msg += 'Проблема с камерой %s' % cam.print_name
                msg += '\n'
                self._logger.error("Problem with a camera %s (%s)" % (cam.print_name, str(e)))
            else:
                msg = '%s получение скриншота...' % cam.print_name
                msg += '\n'
        if msg == "":
            msg = "Камер для скриншота нет"
        context.bot.send_message(chat_id=chat_id, text=msg,
                                 reply_markup=self._access.get_markup(chat_id))
        self._admin_log(update, msg)


class ApiAclCmdPrivateMod(ApiAclCmd):
    name = 'private'

    def do(self, update: Update, context: CallbackContext):
        if not self._check_access(update):
            return
        if self._access.is_norm_mode:
            if len(context.args) > 0:
                hours = float(context.args[0])
            else:
                hours = 0.5
            msg = "Приватный режим включен на %i секунд" % int(hours * 3600)
            self._access.set_private_mode(hours * 3600)
        elif self._access.is_private_mode:
            msg = "Приватный режим выключен"
            self._access.set_norm_mode()
        else:
            msg = "Текущий режим не нормальный"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg,
                                 reply_markup=self._access.get_markup(update.effective_chat.id))
        self._admin_log(update, msg)
