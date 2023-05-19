import socket
import socketserver
import threading

from server.HttpTool import HttpHandler


class SimTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            # 接收客户端请求数据
            client_addr = self.client_address
            request_data = self.request.recv(2048).decode()
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


def run_server(host: str, port: int, max_thread: int = 10, default_timeout=2):
    # 设置TCP超时
    socket.setdefaulttimeout(default_timeout)

    # 设置最大线程数
    SimTCPServer.set_max_thread(max_thread)

    # 创建服务器
    server = SimTCPServer((host, port), SimTCPHandler)

    print(f'Server start at {host}:{port}.')
    try:
        # 启动服务器
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server start to stop.Please wait...')
        server.shutdown()
