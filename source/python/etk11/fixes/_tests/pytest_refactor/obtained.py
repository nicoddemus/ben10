from coilib50.basic import Reraise
from coilib50.basic.interface import Interface
from coilib50.cache.memoize import Memoize
from coilib50.cache import memoize
from coilib50.filesystem import FindFiles
import coilib50.filesystem


@memoize.Memoize()
def Method(input):
    try:
        pass
    except Exception:
        Reraise(e, '')
