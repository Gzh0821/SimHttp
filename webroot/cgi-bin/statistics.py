import psutil
import sys
from CgiTool.ArgTool import ArgCgi
import platform


class StatCgi(ArgCgi):
    def handle(self) -> None:
        try:
            mem = psutil.virtual_memory().percent
            self.add_output('mem_percent', f'{mem}%')
            self.add_output('python_version', sys.version)
            self.add_output('server_system', f'{platform.system()}/{platform.version()}')
        except Exception:
            return


if __name__ == '__main__':
    StatCgi(sys.argv).run()
