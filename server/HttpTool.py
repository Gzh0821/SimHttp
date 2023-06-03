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

from server.FileTool import FileReader, ExecHandler
import re
import datetime
import user_agents
from server.LogTool import Logger
from server.ConfigTool import GlobalConfig as Config


class HttpHandler:
    head_dict = {200: 'HTTP/1.1 200 OK', 400: 'HTTP/1.1 400 Bad Request',
                 403: 'HTTP/1.1 403 Forbidden', 404: 'HTTP/1.1 404 Not Found',
                 418: 'HTTP/1.1 418 I\'m a teapot'}
    default_responds_headers = {'Server': 'Gaozih SimHttp/1.0.0 (Python3)',
                                'Sim-Test': 'True',
                                'Connection': 'Keep-Alive'
                                }

    @classmethod
    def handle(cls, request_data: str, client_addr: tuple[str, int]) -> bytes:
        time_start = datetime.datetime.now()
        request_lines = request_data.split('\r\n')
        default_dynamic_para = {}
        print(f'--------')
        now_time_str = time_start.strftime("%Y-%b-%d %H:%M:%S")
        if not cls.check(request_lines):
            response_status = 400
            request_method = 'GET'
            response_body, response_type = FileReader.read_400()
            Logger.write(client_addr[0], client_addr[1], now_time_str, '', '', 400,
                         len(response_body), response_type, '')
            if_dynamic = False
        else:
            request_method, path, http_version = request_lines[0].split()
            request_headers, request_content = cls.phrase(request_lines[1:])

            print(f'请求方法：{request_method}, 请求路径：{path}, HTTP版本：{http_version}')
            if 'User-Agent' in request_headers:
                print(f"用户头：{request_headers['User-Agent']}")
                # 向所有动态页面发送的信息：
                default_dynamic_para['__client_origin_user_agent__'] = request_headers['User-Agent']
                user_agent = user_agents.parse(request_headers['User-Agent'])
                default_dynamic_para['__client_os__'] = user_agent.os.family
                default_dynamic_para['__client_browser__'] = user_agent.browser.family
                default_dynamic_para['__client_device__'] = user_agent.device.family
                default_dynamic_para['__client_user_agent__'] = str(user_agent)
            default_dynamic_para['__server_time__'] = now_time_str
            default_dynamic_para['__client_ip__'] = client_addr[0]
            default_dynamic_para['__client_port__'] = str(client_addr[1])
            default_dynamic_para['__request_method__'] = request_method
            # 构造响应数据
            if request_method in ('GET', 'HEAD'):
                ret_para, if_dynamic = ExecHandler.handle(path, '', request_method)
            else:
                ret_para, if_dynamic = ExecHandler.handle(path, request_content, request_method)
            response_status, response_body, response_type = FileReader.read(path,
                                                                            {**ret_para, **default_dynamic_para})
            referer = request_headers.get('Referer', '')
            Logger.write(client_addr[0], client_addr[1], now_time_str, request_method, path,
                         response_status, len(response_body), response_type, referer)
        # 响应的开始行
        head_data = cls.head_dict[response_status]
        print(f'响应：{head_data}')
        if not isinstance(response_body, bytes):
            response_body = response_body.encode("utf-8")
        # 组合响应报文
        response_head = f'{head_data}\r\n' \
                        f'{cls.gen_header(len(response_body), response_type, time_start, not if_dynamic)}' \
                        f'\r\n\r\n'.encode("utf-8")
        if request_method == 'HEAD':
            return response_head
        response_data = response_head + response_body

        return response_data

    @classmethod
    def check(cls, request_lines: list[str]) -> bool:
        # 检查开始行是否正确
        request_pattern = r'^[A-Z]+\s\S+\sHTTP\/(1\.0|1\.1|2\.0)$'
        print(request_lines[0])
        if re.match(request_pattern, request_lines[0]):
            try:
                request_method, path, http_version = request_lines[0].split()
            except ValueError as e:
                print(e)
                print(f'-->{request_lines[0]}<--')
            else:
                if request_method in ('GET', 'POST', 'HEAD'):
                    return True
        return False

    @classmethod
    def phrase(cls, header_lines: list[str]) -> tuple[dict[str, str], str]:
        headers = {}
        content = ''
        content_flag = False
        for line in header_lines:
            if not content_flag:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
                elif line == '':
                    content_flag = True
            else:
                content += line
        return headers, content

    @classmethod
    def gen_header(cls, content_len: int, content_type: str, time_start: datetime, if_cache: bool) -> str:
        headers = cls.default_responds_headers.copy()

        time_end = datetime.datetime.now()
        # 获取当前的 UTC 时间
        now = datetime.datetime.utcnow()

        # 将时间格式化成 HTTP 响应头中的日期格式
        date_str = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        headers['Content-Length'] = str(content_len)
        headers['Date'] = date_str
        headers['Content-Type'] = content_type
        headers['Handle-time'] = f'{time_end.microsecond - time_start.microsecond} microsecond'
        headers['Keep-Alive'] = f'timeout={Config.get("default_timeout")}, max=100'
        if if_cache:
            headers['Cache-Control'] = 'max-age=600'
        header_str = '\r\n'.join([f'{key}: {value}' for key, value in headers.items()])
        return header_str
