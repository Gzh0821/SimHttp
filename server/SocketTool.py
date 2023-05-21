import socket
import socketserver
import threading

from server.HttpTool import HttpHandler
from server.SslTool import SimSSLWrapper
from server.ConfigTool import GlobalConfig as Config


class SimTCPHandler(socketserver.BaseRequestHandler):
    ssl_context = None

    @classmethod
    def set_ssl(cls, ssl_context: SimSSLWrapper):
        cls.ssl_context = ssl_context

    def handle(self):
        if Config.if_ssl():
            self.request = self.ssl_context.wrap(self.request)
        try:
            # 接收客户端请求数据
            client_addr = self.client_address
            request_data = self.request.recv(Config.getint('recv_len')).decode()
            res_data = HttpHandler.handle(request_data, client_addr)
            self.request.sendall(res_data)
        except TimeoutError:
            self.request.close()


class SimTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    max_thread_count = 20

    @classmethod
    def set_max_thread(cls, max_thread_count: int):
        cls.max_thread_count = max_thread_count

    def process_request_thread(self, request, client_address):
        # 检查当前活跃的线程数量
        current_thread_count = threading.active_count() - 1  # 减去主线程
        if current_thread_count >= self.max_thread_count:
            # 拒绝新的连接
            print(f'Rejected connection from {client_address}. Maximum thread count reached.')
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
