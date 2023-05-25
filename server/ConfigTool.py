#   Copyright 2023 Gaozih/Gzh0821 https://github.com/Gzh0821
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import configparser
from server.LogTool import Logger


class GlobalConfig:
    config = None
    config_dict = {}
    ssl_stat = False

    @classmethod
    def init(cls, config_path: str):
        cls.config = configparser.ConfigParser()
        cls.config.read(config_path, encoding='utf-8')
        cls.config_path = config_path

        for key, value in cls.config.items('Server'):
            cls.config_dict[key] = value

        if cls.config.getboolean('SSL', 'ssl'):
            for key, value in cls.config.items('SSL'):
                cls.config_dict[key] = value
            cls.ssl_stat = True
        else:
            cls.ssl_stat = False

        Logger.init(cls.get('log_file'))

    @classmethod
    def get(cls, item: str) -> str:
        return cls.config_dict[item]

    @classmethod
    def getint(cls, item: str) -> int:
        return int(cls.config_dict[item])

    @classmethod
    def if_ssl(cls) -> bool:
        return cls.ssl_stat
