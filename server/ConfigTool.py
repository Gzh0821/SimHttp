import configparser


class GlobalConfig:
    config = None
    config_dict = {}

    @classmethod
    def init(cls, config_path: str):
        cls.config = configparser.ConfigParser()
        cls.config.read(config_path, encoding='utf-8')
        cls.config_path = config_path

        for key, value in cls.config.items('Server'):
            cls.config_dict[key] = value

    @classmethod
    def get(cls, item: str):
        return cls.config_dict[item]

    @classmethod
    def getint(cls, item: str):
        return int(cls.config_dict[item])
