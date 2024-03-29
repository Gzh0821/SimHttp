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

import socket
import socketserver
import ssl
import threading

from server.ConfigTool import GlobalConfig as Config
from server.HttpTool import HttpHandler
from server.SslTool import SimSSLWrapper


class SimTCPHandler(socketserver.BaseRequestHandler):
    ssl_context = None

    @classmethod
    def set_ssl(cls, ssl_context: SimSSLWrapper):
        cls.ssl_context = ssl_context

    def handle(self):
        try:
            if Config.if_ssl():
                try:
                    self.request = self.ssl_context.wrap(self.request)
                except ssl.SSLError:
                    # print(f"Wrong request from {self.client_address}")
                    self.request.close()
                    return

            # 接收客户端请求数据
            while True:
                client_addr = self.client_address
                request_data = self.request.recv(Config.getint('recv_len')).decode()
                res_data = HttpHandler.handle(request_data, client_addr)
                self.request.sendall(res_data)
        except TimeoutError:
            # print(f"Close socket {self.client_address}")
            self.request.close()
        except ssl.SSLZeroReturnError:
            # print(f"Close socket {self.client_address}")
            self.request.close()

class SimTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    max_thread_count = 20

    @classmethod
    def set_max_thread(cls, max_thread_count: int):
        cls.max_thread_count = max_thread_count

    def process_request_thread(self, request, client_address):
        # 检查当前活跃的线程数量
        current_thread_count = threading.active_count() - 2  # 减去主线程
        if current_thread_count >= self.max_thread_count:
            # 拒绝新的连接
            # print(f'Rejected connection from {client_address}. Maximum thread count reached.')
            return

        # 处理请求
        super().process_request_thread(request, client_address)


def run_server(host: str, port: int):
    # 设置TCP超时
    socket.setdefaulttimeout(Config.getint('default_timeout'))

    # 设置最大线程数
    SimTCPServer.set_max_thread(Config.getint('max_thread'))

    if Config.if_ssl():
        # 创建SSL隧道
        ssl_context = SimSSLWrapper(Config.get('crt_path'), Config.get('key_path'))
        SimTCPHandler.set_ssl(ssl_context)

    # 创建服务器
    server = SimTCPServer((host, port), SimTCPHandler)

    print(f'Server start at {host}:{port}.')
    try:
        # 启动服务器
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server start to stop.Please wait...')
        server.shutdown()
