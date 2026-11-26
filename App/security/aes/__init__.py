from App.security.aes.enc import e
from App.security.aes.dec import d


class Aes:
    e = staticmethod(e)
    d = staticmethod(d)


aes = Aes
