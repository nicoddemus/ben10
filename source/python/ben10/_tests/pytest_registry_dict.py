import pytest
import sys



#===================================================================================================
# Test
#===================================================================================================
class Test:

    @pytest.mark.skipif("not sys.platform.startswith('win')")
    def testRegistryDict(self):
        from ben10.registry_dict import RegistryDict

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
