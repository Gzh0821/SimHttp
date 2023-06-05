from server.ConfigTool import GlobalConfig as Config
from server.SocketTool import run_server

if __name__ == '__main__':
    Config.init('config.ini')
    run_server('localhost', 32768)
