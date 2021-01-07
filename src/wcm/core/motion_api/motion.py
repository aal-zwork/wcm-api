import re

import requests

from .base import MotionBase
from .cam import Cam, Cams


class Motion(MotionBase):
    def __init__(self, uri: str):
        super(Motion, self).__init__(uri)
        self.cams = Cams()
        try:
            resp = requests.get(self.uri)
        except Exception as e:
            self._logger.warning('HTTP Error(%s)' % e)
        else:
            if resp.status_code == 200:
                for cam_id in set(re.findall(r"(?<=camera_click\('cam_)\d+", resp.text)):
                    self.cams.append(Cam(self.uri, int(cam_id)))

    @property
    def is_connect(self):
        try:
            resp = requests.get(self.uri)
        except Exception as e:
            self._logger.warning('HTTP Error(%s)' % e)
            return False
        else:
            return resp.status_code == 200
