from server.SocketTool import *
from server.ConfigTool import GlobalConfig as Config

if __name__ == '__main__':
    Config.init('config.ini')
    run_server('0.0.0.0', 8000)

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
