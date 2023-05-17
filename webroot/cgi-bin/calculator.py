# {%ONLY POST%}
import sys
from CgiTool.ArgTool import ArgCgi


class CalculatorCgi(ArgCgi):
    def handle(self) -> None:
        try:
            first = float(self['first'])
            second = float(self['second'])
            rule = self['rule']
            res = 'Error!'
            if rule == 'add':
                res = first + second
            elif rule == 'multi':
                res = first * second
            self.add_output('result', str(res))
        except Exception as e:
            self.add_output('result', str(e))


if __name__ == '__main__':
    CalculatorCgi(sys.argv).run()
