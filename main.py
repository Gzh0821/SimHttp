from server.SocketTool import *
from server.ConfigTool import GlobalConfig as Config

if __name__ == '__main__':
    Config.init('config.ini')
    run_server('0.0.0.0', 8000)

