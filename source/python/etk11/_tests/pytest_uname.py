from etk11.uname import Platform, SimplePlatform, Distribution, IsRunningOn64BitMachine, GetPlatformShortName, \
    GetPlatformLongName, GetPlatformMneumonic



#=======================================================================================================================
# Test
#=======================================================================================================================
class Test():

    def test_Dist(self):
        import platform
        import sys

        assert isinstance(IsRunningOn64BitMachine(), bool)

        if sys.platform == 'linux2':
            if '64' in platform.machine():
                result = dict(
                    Platform='x86_64.redhat55',
                    SimplePlatform='amd64.redhat',
                    Distribution='redhat55',
                    ShortName='redhat64',
                    LongName='RedHat Linux 64-bit',
                    Mneumonic='r64',
                )
            else:
                result = dict(
                    Platform='i686.redhat46',
                    SimplePlatform='i686.redhat',
                    Distribution='redhat46',
                    ShortName='redhat32',
                    LongName='RedHat Linux 32-bit',
                    Mneumonic='r32',
                )
        else:
            if 'AMD64' in platform.python_compiler():
                result = dict(
                    Platform='amd64.win32',
                    SimplePlatform='amd64.win32',
                    Distribution='win32',
                    ShortName='win64',
                    LongName='Windows 64-bit',
                    Mneumonic='w64',
                )
            else:
                result = dict(
                    Platform='i686.win32',
                    SimplePlatform='i686.win32',
                    Distribution='win32',
                    ShortName='win32',
                    LongName='Windows 32-bit',
                    Mneumonic='w32',
                )

        assert Platform() == result['Platform']
        assert SimplePlatform() == result['SimplePlatform']
        assert Distribution() == result['Distribution']
        assert GetPlatformShortName() == result['ShortName']
        assert GetPlatformLongName() == result['LongName']
        assert GetPlatformMneumonic() == result['Mneumonic']


    def testPlatformNames(self):
        '''
            This test checks if the GetPlatformShortName and GetPlatformLongName
            are working correctly when we give as parameter the desired platform.
        '''
        def CheckPlatformName(platform, expected_results):
            '''
                Method to check the platform names.
                
                :type platform: C{str}
                :param platform:
                    the platform representation.
                
                :type expected_results: dict with keys ShortName and LongName.
                :param expected_results:
                    Each key must have a string with the expected value.
                :type  expected_results: C{dict}
            '''
            assert GetPlatformShortName(platform) == result['ShortName']
            assert GetPlatformLongName(platform) == result['LongName']
            assert GetPlatformMneumonic(platform) == result['Mneumonic']


        # Windows 32 -------------------------------------------------------------------------------
        result = dict(
            ShortName='win32',
            LongName='Windows 32-bit',
            Mneumonic='w32',
        )
        CheckPlatformName('i686.win32', result)

        # Linux 32 ---------------------------------------------------------------------------------
        result = dict(
            ShortName='redhat32',
            LongName='RedHat Linux 32-bit',
            Mneumonic='r32',
        )
        CheckPlatformName('i686.redhat', result)

        # Windows 64 -------------------------------------------------------------------------------
        result = dict(
            ShortName='win64',
            LongName='Windows 64-bit',
            Mneumonic='w64',
            )
        CheckPlatformName('amd64.win32', result)

        # Linux 64 ---------------------------------------------------------------------------------
        result = dict(
            ShortName='redhat64',
            LongName='RedHat Linux 64-bit',
            Mneumonic='r64',
        )
        CheckPlatformName('amd64.redhat', result)
