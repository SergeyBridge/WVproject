import numpy as np
import pandas as pd
from abc import ABC, abstractmethod, abstractproperty


class AbstractDataEngine(ABC):

    @property
    @abstractmethod
    def get_train_df(self):
        pass

    @property
    @abstractmethod
    def get_test_df(self):
        pass


class AdultDataEngine(AbstractDataEngine):
    def __init__(self, train_file, test_file):
        """
        При инициализации в случае неуспеха возвращает исключние от  pandas.read_csv()
        :param train_file: path файла с обучающей выборкой
        :param test_file: path файла с тестовой  выборкой
        """

        try:

            self.train = pd.read_csv(train_file)
            self.test = pd.read_csv(test_file)

        except Exception as e:
            raise e("AdultDataEngine exception")



    @property
    def get_train_df(self):
        """
        property, всегда существует и корректно возвращает
        :return: pandas.DataFrame с обучающей выборкой
        """
        return self.train

    @property
    def get_test_df(self):
        """
        property, всегда существует и корректно возвращает
        :return: pandas.DataFrame с тестовой выборкой
        """
        return self.test


if __name__ == "__main__":
    engine = AdultDataEngine(
        train_file="../../data/adult_dataset/adult.data",
        test_file="../../data/adult_dataset/adult.test")

    train = engine.get_train_df
    test = engine.get_test_df
    print(train.head())
    print(test.head())

