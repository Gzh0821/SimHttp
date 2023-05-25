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

import logging


class Logger:
    @classmethod
    def init(cls, file_name: str):
        logging.basicConfig(filename=file_name, level=logging.INFO)

    @classmethod
    def write(cls, ip_addr: str, ip_port: int, time_str: str, request_type: str, request_file: str,
              status: int, filesize: int, filetype: str, referer: str):

        log_str = f'[INFO][Time#{time_str}][Addr#{ip_addr}:{ip_port}][Type#{request_type}]' \
                  f'[RequestFile#{request_file}]' \
                  f'[Status#{status}][FileSize#{filesize}][FileType#{filetype}][Referer#{referer}]'

        if status == 200:
            logging.info(log_str)
        else:
            logging.error(log_str)
