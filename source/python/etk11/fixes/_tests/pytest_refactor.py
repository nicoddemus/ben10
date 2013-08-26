


pytest_plugins = ["etk11.fixtures"]



#=======================================================================================================================
# Test
#=======================================================================================================================
class Test:

    def testFixEtk11(self, embed_data):
        from lib2to3 import main

        embed_data.CreateDataDir()

        args = ['-w', '-n', '--add-suffix=3', embed_data.GetDataDirectory()]
        main.main('etk11.fixes', args)

        embed_data.AssertEqualFiles('obtained.py3', 'expected.py3')

