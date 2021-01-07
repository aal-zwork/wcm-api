import argparse
import io

import yaml

from .base import BaseService
from .http_server_core import HttpServerCore
from .motion_tool import MotionTool
from .telegram_core import TelegramCore
from ..utils.checkers import argparse_is_path, is_ip, is_uri, is_tg_id, concat_dict


class WcmCore(BaseService):
    def __init__(self):
        super(WcmCore, self).__init__()
        self.config_from_args = self._load_config_from_args()
        self.http_server_core = None
        self.telegram_core = None
        self.motion_tool = None

    def polling(self):
        config_from_file = self._load_config_from_file(self.config_from_args)
        wcm_config = concat_dict(self.config_from_args, config_from_file)
        # print(self.config_from_args)
        # print(config_from_file)
        # print(wcm_config)

        proxy = wcm_config['proxy']
        motion_config = wcm_config['motion']
        telegram_config = wcm_config['telegram']
        http_server_config = wcm_config['http_server']

        uris = motion_config['uris']
        if uris is not None:
            self.motion_tool = MotionTool(uris, motion_config)
            # self._logger.info(self.motion_tool.__dict__)
        else:
            self._logger.warning("Motion uris is not set")

        token = str(telegram_config['token'])
        if token is not None:
            if proxy is not None:
                telegram_config['proxy'] = proxy
            try:
                self.telegram_core = TelegramCore(token, self.motion_tool, telegram_config)
                self.telegram_core.polling()
                # self._logger.info(self.telegram_core.__dict__)
            except Exception as e:
                self._logger.warning("Telegram core is not loaded(%s)" % str(e))
                self.telegram_core = None
        else:
            self._logger.warning("Telegram token is not set")

        listen = str(http_server_config['listen'])
        if listen is not None:
            try:
                self.http_server_core = HttpServerCore(listen, self.telegram_core, self.motion_tool)
                self.http_server_core.polling()
            except Exception as e:
                self._logger.warning("HttpServer core is not loaded(%s)" % str(e))
                self.http_server_core = None
        else:
            self._logger.warning("Telegram token is not set")

    def shutdown(self):
        if self.http_server_core is not None:
            self.http_server_core.shutdown()
        if self.telegram_core is not None:
            self.telegram_core.shutdown()

    @staticmethod
    def _load_config_from_args():
        parser = argparse.ArgumentParser(description='Web Cam Manager')
        parser.add_argument('--config', help='config file path', default=None, type=argparse.FileType('r'))
        parser.add_argument('--listen', help='listen address', default='0.0.0.0:20000', type=is_ip)
        parser.add_argument('--telegram', help='telegram token', default=None, type=is_tg_id)
        parser.add_argument('--motion', help='motion servers', default=None, nargs='+', type=is_uri)
        parser.add_argument('--proxy', help='servers', type=is_uri)
        parser.add_argument('--daemon', help='daemon mode', action='store_true', default=None)
        parser.add_argument('--pid', help='pid file path', default='/var/run/wcm.pid', type=argparse_is_path)
        config_from_args = vars(parser.parse_args())
        config_from_args['http_server'] = {'listen': config_from_args.pop('listen')}
        config_from_args['telegram'] = {'token': config_from_args.pop('telegram')}
        config_from_args['motion'] = {'uris': config_from_args.pop('motion')}
        return config_from_args

    def _load_config_from_file(self, config_from_args):
        config_from_file = {}
        try:
            file = config_from_args['config']
            if isinstance(file, io.TextIOWrapper):
                config_from_file = yaml.load(file, Loader=yaml.FullLoader)
                file.close()
            elif isinstance(file, str):
                with open(file, mode='r') as f:
                    config_from_file = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            self._logger.warning("Error load config from file(%s)" % str(e))

        return config_from_file
