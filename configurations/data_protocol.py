from collections import OrderedDict

import numpy as np
import pandas as pd
import yaml
from abc import ABC


# отладочный код yaml
config_yaml = """
protocol:
  - !fields
    order_id:
      type: Na
      min_val: Na
      max_val: Na
    stat_order_created_ts:
      - type: Na
      - min_val: Na
      - max_val: Na
    stat_order_processed_user_id:
      - type: Na
      - min_val: Na
      - max_val: Na

"""


class AbstractDataProtocol(yaml.YAMLObject):
    """
    Абстрактный класс
    Обработчик YAML
    """

    @classmethod
    def from_yaml(cls, _loader, _node):
        _parser = cls.Parse()
        config = _loader.construct_mapping(_node)
        _parser.config.update(config)

        return _parser

    @classmethod
    def get_parser(cls):
        return cls.Parser()

    class Parse(ABC):
        pass


class GraderDataProtocol(AbstractDataProtocol):
    """
    Обработчик yaml файла с протоколом
    Экземпляр этого  класса создается и  инициализируется loader'ом модуля yaml
    В возвращаемом обьекте загружены все поля протокола и доступны методы их обработки
    см. методы этого класса


    """
    yaml_tag = u"!fields"

    class Parse:
        def __init__(self):
            self.config = OrderedDict()

        def some_method(self):
            print("some method")

        def get_parser(self):
            return self.Parse

        def num(self, series: pd.Series):
            return pd.to_numeric(series)

        def ts(self, series: pd.Series):
            return pd.to_datetime(series, infer_datetime_format=True)

        def str(self, series: pd.Series):
            name = series.name
            if series.name == "order_client_sex":
                pass
            return series.astype(str)

        def Na(self, series: pd.Series):
            return None



if __name__ == "__main__":

    path_to_yaml = "protocol.yaml"

    #with open(path_to_yaml, "r") as protocol:
    #    parser = yaml.load(protocol, Loader=yaml.FullLoader)["protocol"][0]

    parser = yaml.load(config_yaml, Loader=yaml.FullLoader)["protocol"][0]
    print("parser\n")
    print(parser.some_method())
    print(parser.config)
    print(f"\nparser\n")
