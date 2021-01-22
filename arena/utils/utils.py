# simple general purpose functions

class Utils(object):
    @classmethod
    def tuple_to_string(cls, tup, sep=" "):
        """Turns a tuple into a string"""
        s = ""
        for val in tup:
            s += str(val) + sep
        return s.strip()

    @classmethod
    def agran(cls, float_num):
        """Reduces floating point numbers to ARENA granularity"""
        if isinstance(float_num, str):
            try:
                float_num = float(float_num)
            except:
                pass
        return round(float_num, 3)
