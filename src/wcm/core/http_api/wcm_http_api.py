import falcon

from .base import HttpAPI
from ..motion_tool import MotionTool
from ..telegram_core import TelegramCore


class HttpApiWcm(HttpAPI):
    pass


class HttpApiWcmStatus(HttpApiWcm):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        try:
            json_obj = {}
            if isinstance(self.motion_tool, MotionTool):
                json_obj["motion"] = self.motion_tool.cams.status
            else:
                json_obj["motion"] = None

            if isinstance(self.telegram_core, TelegramCore):
                json_obj["telegram"] = self.telegram_core.running
            else:
                json_obj["telegram"] = None
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s(%s)" % (api_msg, str(e))
            self._logger.error(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_500)
        else:
            api_msg = "It is Wcm status"
            log_msg = api_msg
            self._logger.debug(log_msg)
            self._return_api_obj(resp, json_obj, api_msg, falcon.HTTP_200)
