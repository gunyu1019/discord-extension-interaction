
def get_as_snowflake(data, key):
    try:
        value = data[key]
    except KeyError:
        return None
    else:
        return value and int(value)


def get_enum(cls, val):
    enum_val = [i for i in cls if i.value == val]
    if len(enum_val) == 0:
        return val
    return enum_val[0]
