import cgi

import falcon

from .base import HttpAPI
from ..motion_api.cam import Cam
from ..motion_tool import MotionTool, MotionCamNotFoundError


class HttpApiNoMotionException(Exception):
    pass


class HttpApiMotion(HttpAPI):
    pass


class HttpApiMotionConfig(HttpApiMotion):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        try:
            if not isinstance(self.motion_tool, MotionTool):
                raise HttpApiNoMotionException
            json_obj = self.motion_tool.status
        except HttpApiNoMotionException:
            api_msg = "Didn't found"
            log_msg = "Motions is not configure"
            self._logger.warning(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s(%s)" % (api_msg, str(e))
            self._logger.error(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_500)
        else:
            api_msg = "It is MotionTool object"
            log_msg = api_msg
            self._logger.debug(log_msg)
            self._return_api_obj(resp, json_obj, api_msg, falcon.HTTP_200)


class MotionCams(HttpApiMotion):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        try:
            if not isinstance(self.motion_tool, MotionTool):
                raise HttpApiNoMotionException
            json_obj = self.motion_tool.cams.for_json()
        except HttpApiNoMotionException:
            api_msg = "Didn't found"
            log_msg = "Motions is not configure"
            self._logger.warning(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s(%s)" % (api_msg, str(e))
            self._logger.error(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_500)
        else:
            api_msg = "It is Cams object"
            log_msg = api_msg
            self._logger.debug(log_msg)
            self._return_api_obj(resp, json_obj, api_msg, falcon.HTTP_200)


class HttpApiMotionCamStatus(HttpApiMotion):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response, wcm_cam_id: int):
        print_name = Cam.make_print_name(wcm_cam_id=str(wcm_cam_id))
        try:
            if not isinstance(self.motion_tool, MotionTool):
                raise HttpApiNoMotionException
            cam = self.motion_tool.find_cam_by_wcm_cam_id(wcm_cam_id)
            status = cam.check_status()
        except HttpApiNoMotionException:
            api_msg = "Didn't found"
            log_msg = "Motions is not configure"
            self._logger.warning(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        except MotionCamNotFoundError:
            api_msg = "Didn't found"
            log_msg = "%s by %s" % print_name
            self._logger.debug(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s by %s(%s)" % (api_msg, print_name, str(e))
            self._logger.error(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_500)
        else:
            api_msg = "Cam %s status is %s" % (cam.print_name, status)
            log_msg = api_msg
            self._logger.debug(log_msg)
            ret_obj = {'name': cam.name, 'wcm_cam_id': cam.wcm_cam_id, 'status': status}
            self._return_api_obj(resp, ret_obj, api_msg, falcon.HTTP_200)


class HttpApiMotionCamStart(HttpApiMotion):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response, wcm_cam_id: int):
        print_name = Cam.make_print_name(wcm_cam_id=str(wcm_cam_id))
        if not isinstance(self.motion_tool, MotionTool):
            api_msg = "Didn't found"
            log_msg = "Motions is not configure"
            self._logger.warning(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        else:
            try:
                cam = self.motion_tool.find_cam_by_wcm_cam_id(wcm_cam_id)
                change_status = cam.start()
            except MotionCamNotFoundError:
                api_msg = "Didn't found"
                log_msg = "%s by %s" % print_name
                self._logger.debug(log_msg)
                self._return_api_err(resp, api_msg, falcon.HTTP_401)
            except Exception as e:
                api_msg = "Error make response"
                log_msg = "%s by %s(%s)" % (api_msg, print_name, str(e))
                self._logger.error(log_msg)
                self._return_api_err(resp, api_msg, falcon.HTTP_500)
            else:
                api_msg = "Cam wcm %s change status is %s" % (cam.print_name, change_status)
                log_msg = api_msg
                self._logger.debug(log_msg)
                self._return_api_obj(resp, change_status, api_msg, falcon.HTTP_200)


class HttpApiMotionCamPause(HttpApiMotion):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response, wcm_cam_id: int):
        print_name = Cam.make_print_name(wcm_cam_id=str(wcm_cam_id))
        try:
            if not isinstance(self.motion_tool, MotionTool):
                raise HttpApiNoMotionException
            cam = self.motion_tool.find_cam_by_wcm_cam_id(wcm_cam_id)
            change_status = cam.pause()
        except HttpApiNoMotionException:
            api_msg = "Didn't found"
            log_msg = "Motions is not configure"
            self._logger.warning(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        except MotionCamNotFoundError:
            api_msg = "Didn't found"
            log_msg = "%s by %s" % print_name
            self._logger.debug(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_401)
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s by %s(%s)" % (api_msg, print_name, str(e))
            self._logger.error(log_msg)
            self._return_api_err(resp, api_msg, falcon.HTTP_500)
        else:
            api_msg = "Cam wcm %s change status is %s" % (cam.print_name, change_status)
            log_msg = api_msg
            self._logger.debug(log_msg)
            self._return_api_obj(resp, change_status, api_msg, falcon.HTTP_200)


# Callbacks

class HttpApiCbMotionStart(HttpApiMotion):
    # noinspection PyUnusedLocal
    def on_get(self, req: falcon.Request, resp: falcon.Response, motion_name: str, cam_id: int):
        print_name = Cam.make_print_name(motion_name=motion_name, cam_id=str(cam_id))
        try:
            if not isinstance(self.motion_tool, MotionTool):
                raise HttpApiNoMotionException
            cam = self.motion_tool.find_cam_by_cam_id(motion_name, cam_id)
        except HttpApiNoMotionException:
            api_msg = "Didn't found"
            log_msg = "Motions is not configure"
            tg_msg = "Есть движение на неизвестной камере %s:" % print_name
            self._logger.warning(log_msg)
            self._return_notify_err(resp, api_msg, tg_msg, falcon.HTTP_401)
        except MotionCamNotFoundError:
            api_msg = "Didn't found"
            log_msg = "%s by cam %s" % (api_msg, print_name)
            tg_msg = "Есть движение на неизвестной камере %s" % print_name
            self._logger.debug(log_msg)
            self._return_notify_err(resp, api_msg, tg_msg, falcon.HTTP_401)
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s by cam %s(%s)" % (api_msg, print_name, str(e))
            tg_msg = "Ошибка во время обработки обращения наличия движения от камеры %s:" % print_name
            self._logger.error(log_msg)
            self._return_notify_err(resp, api_msg, tg_msg, falcon.HTTP_500)
        else:
            api_msg = "Detect motion"
            log_msg = "%s on %s" % (api_msg, cam.print_name)
            tg_msg = "Есть движение на камере %s" % cam.print_name
            self._logger.debug(log_msg)
            self._return_notify_obj(resp, True, api_msg, tg_msg, falcon.HTTP_200)


class HttpApiCbMotionPictureUpload(HttpApiMotion):
    CHUNK_SIZE_BYTES = 4096

    def on_post(self, req: falcon.Request, resp: falcon.Response, motion_name: str, cam_id: int):
        print_name = Cam.make_print_name(motion_name=motion_name, cam_id=str(cam_id))
        try:
            if not isinstance(self.motion_tool, MotionTool):
                raise HttpApiNoMotionException
            image = req.get_param('image')
            cam = self.motion_tool.find_cam_by_cam_id(motion_name, cam_id)
        except HttpApiNoMotionException:
            api_msg = "Didn't found"
            log_msg = "Motions is not configure"
            tg_msg = "Есть движение на неизвестной камере %s:" % print_name
            self._logger.warning(log_msg)
            self._return_notify_err(resp, api_msg, tg_msg, falcon.HTTP_401)
        except MotionCamNotFoundError:
            api_msg = "Didn't found"
            log_msg = "%s by cam %s" % (api_msg, print_name)
            tg_msg = "Есть движение на неизвестной камере %s" % print_name
            self._logger.debug(log_msg)
            self._return_notify_err(resp, api_msg, tg_msg, falcon.HTTP_401)
        except Exception as e:
            api_msg = "Error make response"
            log_msg = "%s by cam %s(%s)" % (api_msg, print_name, str(e))
            tg_msg = "Ошибка во время обработки обращения наличия движения от камеры %s:" % print_name
            self._logger.error(log_msg)
            self._return_notify_err(resp, api_msg, tg_msg, falcon.HTTP_500)
        else:
            api_msg = "Detect motion"
            log_msg = "%s on %s" % (api_msg, cam.print_name)
            tg_msg = "Скриншот камеры %s" % cam.print_name
            self._logger.debug(log_msg)
            if isinstance(image, cgi.FieldStorage):
                self.telegram_core.send_img(image.file, tg_msg)
            self._return_notify_obj(resp, True, api_msg, None, falcon.HTTP_200)
