Данные
====================

.. jupyter-execute::
    :hide-code:

    import pandas as pd
    import numpy as np

    path = "../../data/real_2019-12-01-2019-12-31.csv"

    data = pd.read_csv(path, sep=";", )




.. jupyter-execute::

    paid = data['stat_delivery_is_paid'].count()
    returned = data['stat_delivery_is_return'].count()

    p = data['stat_delivery_is_paid']
    r = data['stat_delivery_is_return']

    series = pd.Series(data=[paid, returned, paid+returned,
                             data.shape[0], paid+returned - data.shape[0]])
    series.index = ["p", "r", "p+r", "всего данных", "где то потерялось "]

    print(series)

