from server.ConfigTool import GlobalConfig as Config
from server.SocketTool import run_server

if __name__ == '__main__':
    Config.init('config.ini')
    if Config.ssl_stat:
        run_server('localhost', 443)
    else:
        run_server('localhost', 80)
