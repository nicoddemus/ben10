from sharedscripts10.shared_scripts.esss_project import EsssProject
from sharedscripts10.namespace.namespace_types import PATH, PATHLIST


#===================================================================================================
# Ben10
#===================================================================================================
class Ben10(EsssProject):

    NAME = 'ben10'
    DEPENDENCIES = [
        'ftputil',
        'ordereddict',
        'path_py',
        'pyftpdlib',
        'pylint',
        'pytest',
        'pytest_cov',
        'pytest_localserver',
        'rarfile',
        'windows:pywin32',
    ]

    NAMESPACE_VARIABLES = {
        '$PYTHON3PATH' : PATHLIST('`self.python_dir`')
    }
