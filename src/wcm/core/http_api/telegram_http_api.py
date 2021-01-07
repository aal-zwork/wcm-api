import falcon

from .base import HttpAPI
from ..telegram_core import TelegramCore


class HttpApiNoTelegramException(Exception):
    pass


class HttpApiTelegram(HttpAPI):
    pass


class HttpApiTelegramStatus(HttpApiTelegram):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        try:
            if not isinstance(self.telegram_core, TelegramCore):
                raise HttpApiNoTelegramException
            json_obj = self.telegram_core.status
        except HttpApiNoTelegramException:
            api_msg = "Didn't found"
            log_msg = "Telegram is not configure"
            self._logger.warning(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s(%s)" % (api_msg, str(e))
            self._logger.error(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_500)
        else:
            api_msg = "It is Telegram object"
            log_msg = api_msg
            self._logger.debug(log_msg)
            self._return_api_obj(resp, json_obj, api_msg, falcon.HTTP_200)


class HttpApiTelegramPrivateModeOn(HttpApiTelegram):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response, seconds: int):
        try:
            if not isinstance(self.telegram_core, TelegramCore):
                raise HttpApiNoTelegramException
            json_obj = self.telegram_core.private_mode_on(seconds)
        except HttpApiNoTelegramException:
            api_msg = "Didn't found"
            log_msg = "Telegram is not configure"
            self._logger.warning(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s(%s)" % (api_msg, str(e))
            self._logger.error(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_500)
        else:
            api_msg = "Private mode activate"
            log_msg = api_msg
            self._logger.debug(log_msg)
            self._return_api_obj(resp, json_obj, api_msg, falcon.HTTP_200)


class HttpApiTelegramPrivateModeOff(HttpApiTelegram):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        try:
            if not isinstance(self.telegram_core, TelegramCore):
                raise HttpApiNoTelegramException
            json_obj = self.telegram_core.private_mode_off()
        except HttpApiNoTelegramException:
            api_msg = "Didn't found"
            log_msg = "Telegram is not configure"
            self._logger.warning(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s(%s)" % (api_msg, str(e))
            self._logger.error(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_500)
        else:
            api_msg = "Private mode disable"
            log_msg = api_msg
            self._logger.debug(log_msg)
            self._return_api_obj(resp, json_obj, api_msg, falcon.HTTP_200)
