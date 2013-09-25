from ben10.registry_dict import RegistryDict
import pytest
import sys



#===================================================================================================
# Test
#===================================================================================================
class Test:

    def testRegistryDict(self):
        key = r'Software\Microsoft\Windows NT\CurrentVersion'
        invalid_key = r'INVALID'

        reg = RegistryDict()
        try:
            value = reg[key]

            assert value['CurrentVersion'] == u'6.1'
            assert reg.has_key(key) == True
            assert reg.has_key(invalid_key) == False
            assert key in reg
            assert invalid_key not in reg
        finally:
            reg.close()



#===================================================================================================
# Entry Point
#===================================================================================================
if __name__ == '__main__':
    # Executes with specific coverage.
    retcode = pytest.main(['--cov-report=term-missing', '--cov=ben10.registry_dict', __file__])
    sys.exit(retcode)
