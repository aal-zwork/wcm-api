import json

import falcon

from ..motion_tool import MotionTool
from ..telegram_core import TelegramCore
from ...lg import LgClass


class HttpModules:
    def __init__(self, telegram_core: TelegramCore, motion_tool: MotionTool):
        self.telegram_core = telegram_core
        self.motion_tool = motion_tool


class HttpAPI(LgClass):
    test_foo = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]

    def __init__(self, modules: HttpModules):
        super(HttpAPI, self).__init__()
        self.modules = modules
        self.telegram_core = modules.telegram_core
        self.motion_tool = modules.motion_tool
        self._obj_resp_body = '{ "type": "object", "object":%s, "msg":"%s" }'
        self._err_resp_body = '{ "type": "error", "msg":"%s" }'
        self._wrn_resp_body = '{ "type": "warning", "msg":"%s" }'

    def _return_api_obj(self, resp: falcon.Response, obj: object, msg: str, http_status: str):
        resp.body = self._obj_resp_body % (json.dumps(obj, default=lambda o: str(o)), msg)
        resp.status = http_status

    def _return_api_err(self, resp: falcon.Response, msg: str, http_status: str):
        resp.body = self._err_resp_body % msg
        resp.status = http_status

    def _return_api_wrn(self, resp: falcon.Response, msg: str, http_status: str):
        resp.body = self._wrn_resp_body % msg
        resp.status = http_status

    def _return_notify_obj(self, resp: falcon.Response, obj: object, msg: str, msg_ru: str or None, http_status: str):
        if msg_ru is not None:
            if isinstance(self.telegram_core, TelegramCore):
                self.telegram_core.send_msg_all(msg_ru)
        self._return_api_obj(resp, obj, msg, http_status)

    def _return_notify_err(self, resp: falcon.Response, msg: str, msg_ru: str or None, http_status: str):
        if msg_ru is not None:
            if isinstance(self.telegram_core, TelegramCore):
                self.telegram_core.send_msg_all(msg_ru)
        self._return_api_err(resp, msg, http_status)

    def _return_notify_wrn(self, resp: falcon.Response, msg: str, msg_ru: str or None, http_status: str):
        if msg_ru is not None:
            if isinstance(self.telegram_core, TelegramCore):
                self.telegram_core.send_msg_all(msg_ru)
        self._return_api_wrn(resp, msg, http_status)
