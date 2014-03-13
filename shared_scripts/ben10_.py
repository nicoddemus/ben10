from sharedscripts10.namespace.namespace_types import PATH, PATHLIST
from sharedscripts10.shared_scripts.esss_project import EsssProject


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
        'pytest_xdist',
        'pytest_localserver',
        'rarfile',
        'windows:pywin32',
    ]

    NAMESPACE_VARIABLES = {
        '$PYTHON3PATH' : PATHLIST('`self.python_dir`')
    }


    def _GetPackageFileMapping(self):
        return [
            ('`self.working_dirname`/shared_scripts/', '+`self.working_dir`/shared_scripts/*.py'),
            ('`self.working_dirname`/source/python/', '+`self.python_dir`/*.py'),
        ]
