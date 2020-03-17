import numpy as np
import pandas as pd
import yaml
from abc import ABC, abstractmethod, abstractproperty
from catboost import Pool

from configurations import data_protocol


class AbstractDataEngine(ABC):
    """
    - абстрактный класс для всех источников данных и всех моделей
    - дополнительные методы для конкретной модели реализуются  в конкретном классе

    """

    # todo Юниттесты для истоочников данных

    @property
    @abstractmethod
    def Xtrain_df(self):
        """
        """
        pass

    @property
    @abstractmethod
    def Xtest_df(self):
        """
        """
        pass

    @property
    @abstractmethod
    def ytrain_df(self):
        """
        :return: pandas.Series cодержит метку для обучающей выборки
        """

    @property
    @abstractmethod
    def ytest_df(self):
        """
        :return: pandas.Series cодержит метку для тестовой выборки
        """


class RealDataEngineCatboost(AbstractDataEngine):
    """
    - Источник данных между real и моделями Catboost
        - на вход принимает имя файла, предназначен для обучения модели
        - При инициализации в случае неуспеха чтения файла возвращает исключение от  pandas.read_csv()
        - Делит выборку на обучающую и контрольную **1/test_fraction** датчиком случайных величин
        - делает бинарную метку y_target
        - "размеченный на Xtrain, ytrain, Xtest, ytest Dataframe создаётся в конструкторе, \
        с ним можно работать из jupyter
        - Pool для catboost создается вызовом отдельного метода, catboost. \
        Pool - это родной формат для catboost, данные в этом формате подаются на вход модели
        - Pool можно сохранить в файл, после этого убить обьект RealDataEngineCatboost, \
        а на вход catboost подать имя файла с пулом

    :param data_file: path файла с выборкой,
    """

    def __init__(self, data_file, protocol_file, test_fraction=None):

        # Делитель на выборки train, test, показывает, какая часть выборки станет контрольной,
        # остальная часть станет обучающей, например  1/3
        self._test_fraction = test_fraction

        try:

            _raw_data = pd.read_csv(data_file, sep=";", low_memory=False, index_col="order_id")

            self._data = pd.DataFrame()

        except Exception as e:
            raise e("RealDataEngineCatboost data_file absent or invalid")

        try:

            """открываем и парсим файл протокола
            в обьекте parser есть python-словарь с протоколом
            и методы для обработки данных по этому протоколу
            """
            with open(protocol_file, "r") as protocol:
                parser = yaml.load(protocol, Loader=yaml.FullLoader)["protocol"]

            for col, series in _raw_data.items():
                """
                получаем из объекта parser метод для преобразования типа
                метод называется также, как тип поля в протоколе
                например, если тип данных в протоколе указан "num", 
                вызывает метод parser.num() 
                """
                handle_type = parser.__getattribute__(parser.config[col]["type"])
                handle_minval = parser.__getattribute__(parser.config[col]["min_val"])
                handle_maxval = parser.__getattribute__(parser.config[col]["max_val"])

                self._data[col] = handle_type(series)

        except Exception as e:
            raise e("RealDataEngineCatboost protocol_file absent or invalid")

        # выделяем категориальные признаки, т.е. все признаки типа str
        self._cat_features_names = [col for col, series in self._data.items()
                                    if type(series.iloc[1]) == str]

        # вспомогательное деление на train test, вне __init__  переменные недоступны
        train, test = self._split_train_test(self._data)

        """
        Xtrain, Xtest, ytrain, ytest - Dataframe'мы с признаками и метками
        доступны в jupyter для анализа 
        """

        self._Xtrain, self._ytrain = self._make_XY(train)
        self._Xtest, self._ytest = self._make_XY(test)

        self._train_pool = None
        self._test_pool = None

    @property
    def Xtrain_df(self):
        """
        pandas.DataFrame с обучающей выборкой, метка удалена
        :return:
        """
        return self._Xtrain

    @property
    def ytrain_df(self):
        """

        :return: pandas.Series cодержит метку для обучающей выборки
        """
        return self._ytrain

    @property
    def Xtest_df(self):
        """
        pandas.DataFrame с тестовой выборкой, метка удалена
        :return:
        """
        return self._Xtest

    @property
    def ytest_df(self):
        """

        :return: pandas.Series cодержит метку для тестовой выборки
        """
        return self._ytest

    def train_pool(self, force=False):
        """
        - Объект Pool - это внутренний формат данных для catboost, \
        DataEngine преобразует данные в этот формат при необходимости можно сохранить в файл

        - идемпотентно, при повторном вызове не пересобирает пул, возвращает существующий

        :param force: пересобрать пул признаков насильно, прошлый уничтожить, default=False


        :return: Pool с обучающей выборкой (метка удалена), меткой и категориальными признаками
        """
        if force or (self._train_pool is None):
            # self._cat_features = [self._Xtrain.columns.get_loc(x) for x in self._cat_features_names]
            self._train_pool = Pool(data=self._Xtrain, label=self._ytrain,
                                    has_header=True, cat_features=self._cat_features_names,
                                    thread_count=-1)

        return self._train_pool

    def test_pool(self, force=False):
        """
        - Объект Pool - это внутренний формат данных для catboost, \
        DataEngine преобразует данные в этот формат при необходимости можно сохранить в файл

        - иначе None, если при инициализации класса параметр _test_fraction не задавался и выборка \
        на тестовую и обучающую не делилась

        - идемпотентно, при повторном вызове не пересобирает пул, возвращает существующий

        :param force: пересобрать пул признаков насильно, прошлый уничтожить, default=False

        :return: Pool с тестовой выборкой, меткой и категориальными признаками, если тестовая выборка определана,

        """

        # todo Возможна ситуация, когда test_pool не нужен и его не существует, подумать, что должно возвращаться

        if self._test_fraction is None:
            return None

        if force or (self._train_pool is None):
            # создаем
            self.test_pool = Pool(data=self._Xtest, label=self._ytest,
                                  has_header=True, cat_features=self._cat_features_names, thread_count=4)

        return self.test_pool

    def _split_train_test(self, dat):
        """
        Внутренний метод
        Делит выборку на train test, применяется до выделения метки
        Для деления использует случайный датчик из pandas

        :return:  Два Dataframe, [train, test]
        """

        # если не надо делить на train test
        if self._test_fraction is None:
            # Возвращаем пустой Dataframe для теста
            test = pd.DataFrame()

            train = dat
        else:
            frac = 1 / self._test_fraction

            test = dat.sample(frac=frac)

            train_ind = dat.index.drop(test.index)
            train = dat.loc[train_ind]

        return train, test

    def _make_XY(self, splitted_dat):
        """
        - Внутренний метод

        Выделяет обучающую метку из данных. \
        Удаляет метку из признаков
            - Xdata - признаки, метка удалена, pandas.Dataframe, матрица
            - y     - метка, pandas.Series, вектор

        :param spllitted_dat: Dataframe c сырыми данными

        :return: list(Xdata, y)
        """

        splitted_dat["stat_delivery_is_return"].fillna(value=0, inplace=True)
        splitted_dat["stat_delivery_is_paid"].fillna(value=0, inplace=True)

        splitted_dat.loc[:, "stat_delivery_is_return"] = -splitted_dat["stat_delivery_is_return"]

        binary_target = splitted_dat.pop("stat_delivery_is_paid").add(
            splitted_dat.pop("stat_delivery_is_return")).astype(int)

        return splitted_dat, binary_target


if __name__ == "__main__":
    data_file = "/home/sergey/mnt/st1500/Usr/Sergey/TheJob/clientsProjects/data/Webvork/real_2019-12-01-2019-12-31.csv"
    protocol_file = "/home/sergey/mnt/st1500/Usr/Sergey/TheJob/clientsProjects/WVproject/configurations/protocol.yaml"
    engine = RealDataEngineCatboost(
        data_file=data_file, protocol_file=protocol_file,
        test_fraction=3)

    train_pool = engine.train_pool()
    test_pool = engine.test_pool()
