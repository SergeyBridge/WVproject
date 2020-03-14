import numpy as np
import pandas as pd
from abc import ABC, abstractmethod, abstractproperty
from catboost import Pool

class AbstractDataEngine(ABC):
    """
    - абстрактный класс для всех источников данных и всех моделей
    - дополнительные методы для конкретной модели реализуются  в конкретном классе

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


class RealDataEngineCatboost():
    """
    - Источник данных между real и моделями Catboost
        - При инициализации в случае неуспеха возвращает исключение от  pandas.read_csv()
        - Делит выборку на обучающую и контрольную **1/test_fraction** датчиком случайных величин
        - делает бинарную метку y_target
        - размеченный на Xtrain, ytrain, Xtest, ytest Dataframe создаётся в конструкторе, с ним можно работать из jupyter
        - Pool для catboost создается вызовом отдельного метода, catboost.Pool - это родной формат для catboost, данные в этом формате подаются на вход модели
        - Pool можно сохранить в файл, после этого убить обьект RealDataEngineCatboost, а на вход catboost подать имя файла с пулом

    :param data_file: path файла с выборкой,
    """

    def __init__(self, data_file, test_fraction=None):

        # Делитель на выборки train, test, показывает, какая часть выборки станет контрольной,
        # остальная часть станет обучающей, например  1/3
        self._test_fraction = test_fraction

        try:

            self._data = pd.read_csv(data_file, sep=";", low_memory=False)

        except Exception as e:
            raise e("RealDataEngineCatboost exception")

        # категориальные признаки, подумать, как внести эти значения в протокол связи
        # или как-то иначе внести в unittests, очень просто запутаться
        self._cat_features_names = [
            'order_id',
            'stat_order_processed_user_id',
            'stat_order_confirmed_user_id',
            'stat_order_operator_id',
            'stat_order_rejection_reason',
            'stat_order_invalid_reason', 'stat_order_country',
            'stat_order_country_ip', 'stat_order_country_phone',
            'stat_order_region', 'stat_order_city',
            'stat_order_payment_method', 'stat_order_phone_geocoder',
            'stat_order_phone_valid', 'stat_order_status_order',
            'stat_order_is_valid', 'stat_order_is_call_fail',
            'stat_order_valid_error', 'stat_order_webmaster_id',
            'stat_order_offer_id', 'stat_order_landing_id',
            'stat_order_prelanding_id',
            'stat_order_good_count', 'stat_order_phone_id', 'stat_order_utm_source',
            'stat_order_utm_medium', 'stat_order_utm_campaign',
            'stat_order_utm_content', 'stat_order_utm_term', 'stat_order_is_prepay',
            'stat_order_landing_currency',
            'stat_order_account_manager_id',
            'stat_order_unique_goods',
            'stat_delivery_good_count',
            'stat_delivery_delivery_status', 'stat_delivery_manager_id',
            'stat_delivery_exception',
            'stat_delivery_operator_status',
            'stat_delivery_google_and_operator_address_match', 'order_client_name',
            'order_client_surname', 'order_client_additional_phone',
            'order_client_age', 'order_client_age_unknown', 'order_client_sex',
            'order_address_country', 'order_address_region', 'order_address_city',
            'order_address_street', 'order_address_house', 'order_address_housing',
            'order_address_apartment', 'order_address_zip_code']

        # вспомогательное деление на train test, вне __init__ они недоступны
        train, test = self._split_train_test(self._data)

        # Xtrain и проч это Dataframe'мы с признаками и метками
        # доступны в jupyter для анализа предобработки
        # потом этот анализ я реализую в методах, формирующих catboost.Pool
        # если не придумаю что-нибудь получше
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

        :return: pandas.Series c меткой для обучающей выборки
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

        :return: pandas.Series c меткой для тестовой выборки
        """
        return self._ytest

    def train_pool(self, force=False):
        """
        - Объект Pool - это внутренний формат данных для catboost, DataEngine преобразует данные в этот формат при необходимости можно сохранить в файл

        :return: Pool с обучающей выборкой (метка удалена), меткой и категориальными признаками
        """
        if force or (not self._train_pool):
            self._cat_features = [self._Xtrain.columns.get_loc(x) for x in self._cat_features_names]

            self._train_pool = Pool(data=self._Xtrain, label=self._ytrain,
                                    has_header=True, cat_features=self._cat_features, thread_count=4)

        return self._train_pool

    def test_pool(self, force=False):
        """
        - Объект Pool - это внутренний формат данных для catboost, DataEngine преобразует данные в этот формат при необходимости можно сохранить в файл

        :return: Pool с тестовой выборкой, меткой и категориальными признаками, если тестовая выборка определана,

        иначе None, если при инизиализации класса
        """

        # todo Возможна ситуация, когда test_pool не нужен и его не существует, подумать, что должно возвращаться

        if self._test_fraction is None:
            return None

        if force or not self._train_pool:
            self._cat_features = [self._Xtest.columns.get_loc(x) for x in self._cat_features_names]

            self.test_pool = Pool(data=self._Xtest, label=self._ytest,
                              has_header=True, cat_features=self._cat_features, thread_count=4)

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
        data_file="/home/sergey/mnt/st1500/Usr/Sergey/TheJob/clientsProjects/data/Webvork/real_2019-12-01-2019-12-31.csv",
        test_fraction=3)

    train_pool = engine.train_pool()


