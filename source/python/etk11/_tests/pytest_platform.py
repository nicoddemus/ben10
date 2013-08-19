import pytest

from etk11.platform_ import Platform, UnknownPlatform


#===================================================================================================
# Test
#===================================================================================================
class Test:

    def testPlatform(self):
        p = Platform('win', '32')
        assert p.name == 'win'
        assert p.bits == '32'
        assert p.debug == False
        assert str(p) == 'win32'
        assert p.AsString(False) == 'win32'
        assert p.AsString(True) == 'win32'
        assert p.GetSimplePlatform() == 'i686.win32'
        assert p.GetBaseName() == 'win32'
        assert p.GetLongName() == 'Windows 32-bit'
        assert p.GetPlatformFlavour() == 'windows'
        assert p.GetMneumonic() == 'w32'

        p = Platform('win', '64', True)
        assert p.name == 'win'
        assert p.bits == '64'
        assert p.debug == True
        assert str(p) == 'win64d'
        assert p.AsString(False) == 'win64d'
        assert p.AsString(True) == 'win64'
        assert p.GetSimplePlatform() == 'amd64.win32'
        assert p.GetBaseName() == 'win64'
        assert p.GetLongName() == 'Windows 64-bit DEBUG'
        assert p.GetPlatformFlavour() == 'windows'
        assert p.GetMneumonic() == 'w64'

        p = Platform.CreateFromString('win32')
        assert str(p) == 'win32'

        p = Platform.CreateFromSimplePlatform('i686.win32')
        assert str(p) == 'win32'

        with pytest.raises(ValueError):
            p = Platform('INVALID', '32')

        with pytest.raises(ValueError):
            p = Platform('win', 'INVALID')

        p = Platform('win', '32')
        p.name = 'INVALID'
        with pytest.raises(UnknownPlatform):
            p.GetSimplePlatform()

        with pytest.raises(UnknownPlatform):
            p.GetPlatformFlavour()

        with pytest.raises(UnknownPlatform):
            p.GetLongName()

        assert p.GetCurrentFlavour() == p.GetCurrentPlatform().GetPlatformFlavour()


    def testGetValidPlatforms(self):
        assert set(Platform.GetValidPlatforms()) == \
            set([
                'darwin32',
                'darwin32d',
                'darwin64',
                'darwin64d',
                'redhat32',
                'redhat32d',
                'redhat64',
                'redhat64d',
                'win32',
                'win32d',
                'win64',
                'win64d',
            ])


    def testCreate(self):
        assert str(Platform.Create('win32')) == 'win32'
        assert str(Platform.Create('i686.win32')) == 'win32'
        assert str(Platform.Create(None)) == str(Platform.GetCurrentPlatform())

        plat = Platform.GetCurrentPlatform()
        assert Platform.Create(plat) is plat


    def testGetOSPlatform(self):
        assert str(Platform.GetOSPlatform()) == 'win64'
