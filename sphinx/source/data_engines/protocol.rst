Протокол
==========

.. jupyter-execute::
    :hide-code:

    import pandas as pd
    import numpy as np

    path = "/home/sergey/mnt/st1500/Usr/Sergey/TheJob/clientsProjects/data/Webvork/real_2019-12-01-2019-12-31.csv"

    data = pd.read_csv(path, sep=";", low_memory=False)


.. jupyter-execute::
    :hide-code:

    print("\n# ".join(["# ",
        "type: обязательный",
            " - 'num' - скаляр, т.е. возможно сравнение на больше-меньше",
            " - 'datetime' - дата и время, округляем до минут, "
            "но если минут нет, например, только часы, то до максимальной оставшейся точности",
            " - 'string' - признак, категориальный, для которого нет метрики сравнения, например id оператора",
            " - 'Na' - not applied, не участвует (пока) в анализе, например, название улицы ",
        "  ",
        "min_val: необязательный"
            " - минимально возможное значение для скаляра, если не скаляр, должен быть опущен или == 'Na' "
            " если не определен или Na, то не проверяется",
            " - 'Na'",
        "  ",
        "max_val: необязательный, аналогично min_val",
        " \n",
    ]))

    for name in data.columns:
        print(F"- {name}:")
        print(f"{' '*2}- type: Na", )
        print(f"{' '*2}- min_val: Na", )
        print(f"{' '*2}- max_val: Na", )


