
def switch_mp(x):
    """
    switch man power
    :param x: input str
    :return: the mp flag
    """

    return {
        'evenStrength': 0,
        'shortHanded': 1,
        'powerPlay': -1
    }.get(x, 2)
