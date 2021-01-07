import logging
import re
from typing import List

import namesgenerator
import requests

from .base import MotionBase


class CamError(ValueError):
    pass


class CamNotFoundError(ValueError):
    pass


class CamConnectionError(ConnectionError):
    pass


class Cam(MotionBase):
    CAM_UNKNOWN = 'UNKNOWN'
    MOTION_CAM_STATUSES = ['ACTIVE', 'PAUSE', 'NOT RUNNING', CAM_UNKNOWN]
    MOTION_CAM_CONNECTIONS = ['Connection OK', 'Lost connection', 'NOT RUNNING', CAM_UNKNOWN]

    def __init__(self, uri: str, cam_id: int):
        super(Cam, self).__init__(uri)
        self.cam_id = cam_id
        self.wcm_cam_id = self.cam_id
        self.name = '%s.%s' % (self.motion_name, namesgenerator.get_random_name())
        self.__cam_statuses = '|'.join(Cam.MOTION_CAM_STATUSES)
        self.__cam_connections = '|'.join(Cam.MOTION_CAM_CONNECTIONS)

    @staticmethod
    def make_print_name(cam_id: str = "", motion_name: str = "", wcm_cam_id: str = "", name: str or None = None):
        if name is None:
            name = '%s.%s' % (motion_name, namesgenerator.get_random_name())
        return "[%s][%s][%s-%s]" % (name, wcm_cam_id, motion_name, cam_id)

    @property
    def print_name(self):
        return "[%s][%i][%s-%i]" % (self.name, self.wcm_cam_id, self.motion_name, self.cam_id)

    def check_conn(self) -> str:
        try:
            resp = requests.get('%s/%s/detection/connection' % (self.uri, self.cam_id))
        except Exception as e:
            self._logger.debug("Cam %s didn't get response(%s)" % (self.print_name, e))
            return self.CAM_UNKNOWN
        else:
            if resp.status_code != 200:
                pattern = 'Camera %s (%s|.+)' % (self.cam_id, self.__cam_connections)
                result = re.findall(pattern, resp.text)
                if len(result) == 1:
                    return result[0]
                self._logger.debug("Cam %s didn't chk conn, result %s more 1" % (self.print_name, result))
                return self.CAM_UNKNOWN
            self._logger.debug("Cam %s didn't chk conn, http code %i" % (self.print_name, resp.status_code))
            return self.CAM_UNKNOWN

    def check_status(self) -> str:
        try:
            resp = requests.get('%s/%s/detection/status' % (self.uri, self.cam_id))
        except Exception as e:
            self._logger.debug("Cam %s didn't get response(%s)" % (self.print_name, e))
            return self.CAM_UNKNOWN
        else:
            if resp.status_code == 200:
                pattern = 'Camera %s Detection status (%s|.+)' % (self.cam_id, self.__cam_statuses)
                result = re.findall(pattern, resp.text)
                if len(result) == 1:
                    return result[0]
                self._logger.debug("Cam %s didn't chk status, result %s more 1" % (self.print_name, result))
                return self.CAM_UNKNOWN
            self._logger.debug("Cam %s didn't chk status, http code %i" % (self.print_name, resp.status_code))
            return self.CAM_UNKNOWN

    def start(self) -> bool:
        try:
            resp = requests.get('%s/%s/detection/start' % (self.uri, self.cam_id))
        except Exception as e:
            self._logger.debug("Cam %s didn't get response(%s)" % (self.print_name, e))
            return False
        else:
            if resp.status_code == 200:
                return True
            self._logger.debug("Cam %s didn't start, http code %i" % (self.print_name, resp.status_code))
            return False

    def pause(self) -> bool:
        try:
            resp = requests.get('%s/%s/detection/pause' % (self.uri, self.cam_id))
        except Exception as e:
            raise CamConnectionError(e)
        else:
            if resp.status_code == 200:
                return True
            self._logger.debug("Cam %s didn't pause, http code %i" % (self.print_name, resp.status_code))
            return False

    def restart(self):
        try:
            resp = requests.get('%s/%s/action/restart' % (self.uri, self.cam_id))
        except Exception as e:
            raise CamConnectionError(e)
        else:
            if resp.status_code == 200:
                return True
            self._logger.debug("Cam %s didn't restart, http code %i" % (self.print_name, resp.status_code))
            return False

    def quit(self):
        try:
            resp = requests.get('%s/%s/action/quit' % (self.uri, self.cam_id))
        except Exception as e:
            raise CamConnectionError(e)
        else:
            if resp.status_code == 200:
                return True
            self._logger.debug("Cam %s didn't quit, http code %i" % (self.print_name, resp.status_code))
            return False

    def end(self):
        try:
            resp = requests.get('%s/%s/action/end' % (self.uri, self.cam_id))
        except Exception as e:
            raise CamConnectionError(e)
        else:
            if resp.status_code == 200:
                return True
            self._logger.debug("Cam %s didn't end, http code %i" % (self.print_name, resp.status_code))
            return False

    def screenshot(self):
        try:
            resp = requests.get('%s/%s/action/snapshot' % (self.uri, self.cam_id))
        except Exception as e:
            raise CamConnectionError(e)
        else:
            if resp.status_code == 200:
                return True
            self._logger.debug("Cam %s didn't screenshot, http code %i" % (self.print_name, resp.status_code))
            return False

    def __repr__(self):
        # return '%s<id %s>' % (super(Cam, self).__repr__(), self.cam_id)
        return str(self.__dict__)


class Cams(list):
    def __init__(self):
        self.logger = logging.getLogger('.'.join([self.__class__.__module__, self.__class__.__name__]))
        super(Cams, self).__init__()

    @property
    def status(self):
        result = {}
        for cam in self:
            try:
                status = cam.check_status()
            except Exception as e:
                self.logger.error("Cam %s have problem(%s)" % (cam.print_name, str(e)))
                result["%s" % cam.print_name] = Cam.CAM_UNKNOWN
            else:
                result["%s" % cam.print_name] = status
        return result

    def for_json(self) -> List[dict]:
        ret = []
        for cam in self:
            ret.append(cam.__dict__)
        return ret

    def find_cam_by_cam_id(self, cam_id: int) -> Cam:
        for cam in self:
            if cam.cam_id == cam_id:
                return cam
        raise CamNotFoundError("Cam by cam_id %i not found" % cam_id)
