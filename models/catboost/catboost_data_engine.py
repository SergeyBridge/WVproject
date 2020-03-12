import numpy as np
import pandas as pd
from abc import ABC, abstractmethod, abstractproperty


class AbstractDataEngine(ABC):
    """
    - абстрактный класс для всех источников данных и всех моделей
    дополнительные методы для конкретной модели реализуются  в конкретном классе
    """

    # todo Юниттесты для истоочников данных

    @property
    @abstractmethod
    def train_df(self):
        """
        """
        pass

    @property
    @abstractmethod
    def test_df(self):
        """
        """
        pass


class AdultDataEngine(AbstractDataEngine):
    def __init__(self, train_file, test_file):
        """
        При инициализации в случае неуспеха возвращает исключение от  pandas.read_csv()

        :param train_file: path файла с обучающей выборкой
        :param test_file: path файла с тестовой  выборкой
        """

        try:

            self.train = pd.read_csv(train_file)
            self.test = pd.read_csv(test_file)

        except Exception as e:
            raise e("AdultDataEngine exception")

    @property
    def train_df(self):
        """
        :return: pandas.DataFrame с обучающей выборкой
        """
        return self.train

    @property
    def test_df(self):
        """

        :return: pandas.DataFrame с тестовой выборкой
        """
        return self.test


class RealDataEngineCatboost(AbstractDataEngine):
    """
    - Источник данных между real и моделями Catboost
        - При инициализации в случае неуспеха возвращает исключение от  pandas.read_csv()
        - Делит выборку на обучающую и контрольную **1/test_fraction** датчиком случайных величин
        - делает бинарную метку y_target

    :param data_file: path файла с выборкой,
    """

    def __init__(self, data_file, test_fraction):

        # Делитель на выборки train, test
        self._test_fraction = test_fraction

        try:

            self._data = pd.read_csv(data_file, sep=";", low_memory=False)

        except Exception as e:
            raise e("RealDataEngineCatboost exception")

        train, test = self._split_train_test(self._data)

        self.Xtrain, self.ytrain = self._make_XY(train)
        self.Xtest, self.ytest = self._make_XY(test)

        # self.train_pool = self._make_train_pool()
        # self.test_pool = self._make_test_pool()

    @property
    def train_df(self):
        """
        :return: pandas.DataFrame с обучающей выборкой
        """
        return self._train

    @property
    def test_df(self):
        """
        :return: pandas.DataFrame с обучающей выборкой
        """
        return self._test

    @property
    def train_pool(self):
        """
        :return: pandas.DataFrame с обучающей выборкой
        """
        return self._train

    @property
    def train_pool(self):
        """
        Объект Pool - это внутренний формат данных для catboost, DataEngine преобразует данные в этот формат
        Сейчас Pool создаётся в оперативной памяти, при необходимости можно сделать файлом

        :return: Pool с обучающей выборкой, меткой и категориальными признаками
        """
        return self._train_pool

    @property
    def test_pool(self):
        """

        :return: Pool с тестовой выборкой, меткой и категориальными признаками
        """
        return self._test_pool

    def _split_train_test(self, dat):
        """
        Внутренний метод
        Делит выборку на train test, применяется до выделения метки
        Для деления использует случайный датчик из pandas

        :return:  Два Dataframe, [train, test]
        """
        frac = 1 / self._test_fraction

        test = dat.sample(frac=frac)

        train_ind = dat.index.drop(test.index)
        train = dat.loc[train_ind]

        return train, test

    def _make_XY(self, splitted_dat):
        """
        Внутренний метод
        Выделяет обучающую метку из данных
        - Удаляет метку из признаков
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
    engine = RealDataEngineCatboost(
        data_file="/home/sergey/mnt/st1500/Usr/Sergey/TheJob/clientsProjects/"
                  "data/Webvork/real_2019-12-01-2019-12-31.csv",
        test_fraction=3)

    test = engine.test_df
    train = engine.train_df

    print(test.shape)
    print("train_shape", train.shape)

    print(test.head())
