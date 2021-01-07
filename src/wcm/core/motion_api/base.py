import re

from ...lg import LgClass


class MotionBase(LgClass):
    def __init__(self, uri: str):
        super(MotionBase, self).__init__()
        self.uri = uri
        self.motion_name = re.sub(r'^https?://([^/:]+(?::\d+)?)(?:/.*)?$', r'\1', uri)
