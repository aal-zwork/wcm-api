import logging
from socketserver import BaseServer
from threading import Thread
from typing import Tuple
from wsgiref import simple_server

import falcon
from falcon_multipart.middleware import MultipartMiddleware

from .base import BaseService
from .http_api import motion_http_api
from .http_api import telegram_http_api
from .http_api import wcm_http_api
from .http_api.base import HttpModules, HttpAPI
from .motion_tool import MotionTool
from .telegram_core import TelegramCore


class HttpServerCore(BaseService):
    def __init__(self, listen: str, telegram_core: TelegramCore, motion_tool: MotionTool):
        super(HttpServerCore, self).__init__()
        self.listen = listen
        modules = HttpModules(telegram_core, motion_tool)
        api = falcon.API(middleware=[MultipartMiddleware()])
        api.add_route('/status', wcm_http_api.HttpApiWcmStatus(modules))
        api.add_route('/private_mode_on/{seconds:int}', telegram_http_api.HttpApiTelegramPrivateModeOn(modules))
        api.add_route('/private_mode_off', telegram_http_api.HttpApiTelegramPrivateModeOff(modules))
        api.add_route('/telegram/status', telegram_http_api.HttpApiTelegramStatus(modules))
        api.add_route('/motion/config', motion_http_api.HttpApiMotionConfig(modules))
        api.add_route('/motion/cams', motion_http_api.MotionCams(modules))
        api.add_route('/motion/cam/status/{wcm_cam_id:int}', motion_http_api.HttpApiMotionCamStatus(modules))
        api.add_route('/motion/cam/start/{wcm_cam_id:int}', motion_http_api.HttpApiMotionCamStart(modules))
        api.add_route('/motion/cam/pause/{wcm_cam_id:int}', motion_http_api.HttpApiMotionCamPause(modules))
        api.add_route('/cb/motion/start/{motion_name}/{cam_id:int}', motion_http_api.HttpApiCbMotionStart(modules))
        api.add_route('/cb/motion/picture/upload/{motion_name}/{cam_id:int}',
                      motion_http_api.HttpApiCbMotionPictureUpload(modules))
        (host, port) = listen.split(':')
        self.httpd = simple_server.make_server(host, int(port), api, handler_class=WCMRequestHandler)
        self.thread = Thread(name="HttpServer", target=self.httpd.serve_forever)

    def polling(self):
        self.thread.start()

    def shutdown(self):
        self.httpd.shutdown()

    @property
    def running(self):
        return self.thread.is_alive()

    def subscribe(self, api: HttpAPI, argv):
        pass

    def unsubscrive(self, api: HttpAPI, argv):
        pass


class WCMRequestHandler(simple_server.WSGIRequestHandler):
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: BaseServer):
        self.logger = logging.getLogger('.'.join([self.__class__.__module__, self.__class__.__name__]))
        super(WCMRequestHandler, self).__init__(request, client_address, server)

    def log_message(self, fmt, *args):
        self.logger.info("%s - - %s" % (self.client_address[0], fmt % args))

    def log_error(self, fmt, *args):
        self.logger.error("%s - - %s" % (self.client_address[0], fmt % args))
