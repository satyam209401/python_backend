from App.security.base64.enc import e
from App.security.base64.des import d


class Base:
    e = staticmethod(e)
    d = staticmethod(d)


base = Base
