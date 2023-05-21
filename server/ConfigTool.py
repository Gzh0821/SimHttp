import configparser


class GlobalConfig:
    config = None
    config_dict = {}
    ssl_stat = False

    @classmethod
    def init(cls, config_path: str):
        cls.config = configparser.ConfigParser()
        cls.config.read(config_path, encoding='utf-8')
        cls.config_path = config_path

        for key, value in cls.config.items('Server'):
            cls.config_dict[key] = value

        if cls.config.getboolean('SSL', 'ssl'):
            for key, value in cls.config.items('SSL'):
                cls.config_dict[key] = value
            cls.ssl_stat = True
        else:
            cls.ssl_stat = False

    @classmethod
    def get(cls, item: str) -> str:
        return cls.config_dict[item]

    @classmethod
    def getint(cls, item: str) -> int:
        return int(cls.config_dict[item])

    @classmethod
    def if_ssl(cls) -> bool:
        return cls.ssl_stat
