from server.FileTool import FileReader, ExecHandler
import re
import datetime
import user_agents


class HttpHandler:
    head_dict = {200: 'HTTP/1.1 200 OK', 400: 'HTTP/1.1 400 Bad Request',
                 403: 'HTTP/1.1 403 Forbidden', 404: 'HTTP/1.1 404 Not Found'}
    default_responds_headers = {'Server': 'Gaozih SimHttp/1.0.0 (Python3)',
                                'Sim-Test': 'True',
                                'Cache-Control': 'max-age=600',
                                }

    @classmethod
    def handle(cls, request_data: str, client_addr: tuple[str, int]) -> bytes:
        time_start = datetime.datetime.now()
        request_lines = request_data.split('\r\n')
        request_method = None
        default_dynamic_para = {}
        print(f'--------')
        if not cls.check(request_lines):
            response_status = 400
            response_body, response_type = FileReader.read_400()
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
            default_dynamic_para['__server_time__'] = datetime.datetime.now().strftime("%Y-%b-%d %H:%M:%S")
            default_dynamic_para['__client_ip__'] = client_addr[0]
            default_dynamic_para['__client_port__'] = str(client_addr[1])
            default_dynamic_para['__request_method__'] = request_method
            # 构造响应数据
            if request_method in ('GET', 'HEAD'):
                ret_path = ExecHandler.handle(path, '', request_method)
            else:
                ret_path = ExecHandler.handle(path, request_content, request_method)
            response_status, response_body, response_type = FileReader.read(path,
                                                                            {**ret_path, **default_dynamic_para})
        # 响应的开始行
        head_data = cls.head_dict[response_status]
        print(f'响应：{head_data}')
        if not isinstance(response_body, bytes):
            response_body = response_body.encode("utf-8")
        # 组合响应报文
        response_head = f'{head_data}\r\n' \
                        f'{cls.gen_header(len(response_body), response_type, time_start)}' \
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
    def gen_header(cls, content_len: int, content_type: str, time_start: datetime) -> str:
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

        header_str = '\r\n'.join([f'{key}: {value}' for key, value in headers.items()])
        return header_str
