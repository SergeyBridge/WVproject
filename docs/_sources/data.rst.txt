Данные
====================

.. jupyter-execute::
    :hide-code:

    import pandas as pd
    import numpy as np

    path = "../../data/real_2019-12-01-2019-12-31.csv"

    data = pd.read_csv(path, sep=";", )




.. jupyter-execute::

    p = data['stat_delivery_is_paid'].count()
    r = data['stat_delivery_is_return'].count()

    series = pd.Series(data={
        "p": p,
        "r": r,
        "p+r": p+r,
        "всего данных": data.shape[0],
        "где-то потерялось": p+r-data.shape[0]
    })

    print(series)

