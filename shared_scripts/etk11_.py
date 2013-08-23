from sharedscripts10.shared_scripts.esss_project import EsssProject


#===================================================================================================
# Etk11
#===================================================================================================
class Etk11(EsssProject):

    NAME = 'etk11'
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
