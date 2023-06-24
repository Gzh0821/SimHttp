import json
from abc import abstractmethod
from urllib.parse import parse_qs


class ArgCgi:
    def __init__(self, arguments: list[str] | str):
        self.content = None
        if isinstance(arguments, str):
            self.content = arguments
        elif len(arguments) > 1:
            self.content = arguments[1]
        self.post_data = parse_qs(self.content)
        self.out_dict: dict = {}

    def __getitem__(self, item_name: str) -> str:
        return self.post_data.get(item_name, [None])[0]

    @abstractmethod
    def handle(self) -> None:
        pass

    def add_output(self, key: str, value: str):
        if isinstance(key, str) and isinstance(value, str):
            self.out_dict[key] = value

    def run(self):
        try:
            self.handle()
            print(json.dumps(self.out_dict))
        except Exception as e:
            return


class ArgGeneralException(RuntimeError):
    pass
