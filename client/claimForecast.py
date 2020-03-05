import argparse


def main(ytarget):
    """
    Function main takes 1 parameter:

    :param ytarget:
        float,
        list of floats [float[, float]]
        .csv file name with floats, separated by commas

    :return:
        None
    """

    return ytarget


def func2(arg1, arg2):
    """
    
    :param arg1:
    :param arg2:
    :return:
    """
    arg1 = arg2
    return arg1


if __name__ == "__main__":
    """ if main   """
    parser = argparse.ArgumentParser(description='claim forecast classifier')
    parser.add_argument('--ytarget', type=int, help='file path to ytarget .csv file format [float[, float]]')
    args = parser.parse_args()
    main(args.ytarget)
