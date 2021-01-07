import re
from typing import List

from .motion_api.cam import Cams, Cam, CamNotFoundError
from .motion_api.motion import Motion
from ..lg import LgClass


class MotionCamNotFoundError(ValueError):
    pass


class MotionTool(LgClass):

    def __init__(self, uris: list, config: dict):
        super(MotionTool, self).__init__()
        self.uris = uris
        self.motions: List[Motion] = []
        self.cams = Cams()
        self.config = config

        for uri in self.uris:
            self.motions.append(Motion(uri))

        for motion in self.motions:
            for cam in motion.cams:
                cam.wcm_cam_id = len(self.cams)
                if 'cam_names' in self.config:
                    motion_names = config['cam_names']
                    if cam.motion_name in motion_names:
                        cam_names = motion_names[cam.motion_name]
                        if cam.cam_id in cam_names:
                            cam.name = cam_names[cam.cam_id]
                self.cams.append(cam)
        self._logger.info(self.cams)

    def find_cam_by_wcm_cam_id(self, wcm_cam_id: int) -> Cam:
        try:
            return self.cams[wcm_cam_id]
        except ValueError:
            raise MotionCamNotFoundError("Cam by wcm_cam_id %i not found" % wcm_cam_id)

    def find_cam_by_cam_id(self, motion_name: str or None, cam_id: int) -> Cam:
        if motion_name is None:
            for motion in self.motions:
                try:
                    cam = motion.cams.find_cam_by_cam_id(cam_id)
                except CamNotFoundError:
                    pass
                else:
                    return cam
        else:
            for motion in self.motions:
                if re.match(rf'^https?://{motion_name}(?:/.*)?$', motion.uri):
                    try:
                        cam = motion.cams.find_cam_by_cam_id(cam_id)
                    except CamNotFoundError:
                        pass
                    else:
                        return cam
        raise MotionCamNotFoundError("Cam by cam_id %s[%i] not found" % (motion_name, cam_id))

    @property
    def status(self):
        return self.__dict__
