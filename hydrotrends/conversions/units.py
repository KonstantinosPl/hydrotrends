def kelvin_to_celsius(k, decimals=2):
    return (k - 273.15).round(decimals)
def celsius_to_kelvin(c, decimals=2):
    return (c + 273.15).round(decimals)


def m_to_mm(var, decimals=2):
    return (var * 1000).round(decimals)
def mm_to_m(var, decimals=4):
    return (var / 1000).round(decimals)
