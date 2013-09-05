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
        'pytest',
        'pytest_cov',
        'pytest_localserver',
        'pywin32',
    ]

    NAMESPACE_VARIABLES = {
    }
