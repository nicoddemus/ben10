from etk11.reraise import Reraise
from etk11.interface import Interface
from etk11.memoize import Memoize
from etk11 import memoize
from etk11.filesystem import FindFiles
import etk11.filesystem


@memoize.Memoize()
def Method(input):
    try:
        pass
    except Exception:
        Reraise(e, '')
