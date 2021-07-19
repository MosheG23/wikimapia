def country_cap(country_name=None):
    """

    :param country_name:
    :return:
    """
    if type(country_name) is str:
        ValueError('Please enter a string!')
    return country_name.title()
