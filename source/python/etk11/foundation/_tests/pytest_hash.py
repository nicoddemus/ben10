from StringIO import StringIO
from etk11.foundation.hash import DumpDirHashToStringIO, Md5Hex



pytest_plugins = ["etk11.fixtures"]



#===================================================================================================
# Test
#===================================================================================================
class Test():

    def testMd5Hash(self, embed_data):
        embed_data.CreateDataDir()

        stringio = StringIO()
        DumpDirHashToStringIO(embed_data.GetDataDirectory(), stringio, 'bin')
        val = stringio.getvalue()
        assert val.splitlines() == [
            'bin/file1.txt=4124bc0a9335c27f086f24ba207a4912',
            'bin/file2.txt=633de4b0c14ca52ea2432a3c8a5c4c31'
        ]

        stringio = StringIO()
        DumpDirHashToStringIO(embed_data.GetDataDirectory(), stringio, 'bin', exclude='*1.txt')
        val = stringio.getvalue()
        assert val.splitlines() == [
            'bin/file2.txt=633de4b0c14ca52ea2432a3c8a5c4c31'
        ]

        stringio = StringIO()
        DumpDirHashToStringIO(embed_data.GetDataDirectory(), stringio, '', exclude='*1.txt')
        val = stringio.getvalue()
        assert val.splitlines() == [
            'file2.txt=633de4b0c14ca52ea2432a3c8a5c4c31'
        ]

        stringio = StringIO()
        DumpDirHashToStringIO(embed_data.GetDataDirectory(), stringio, '', include='*1.txt')
        val = stringio.getvalue()
        assert val.splitlines() == [
            'file1.txt=4124bc0a9335c27f086f24ba207a4912',
        ]


    def testMd5Hex(self):
        assert Md5Hex(contents='alpha, bravo') == '2c0d78abb6e32d1614a17c6d0e4391c0'

