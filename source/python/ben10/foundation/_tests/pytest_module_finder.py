from ben10.foundation.module_finder import ModuleFinder



pytest_plugins = ["ben10.fixtures"]


#===================================================================================================
# Test
#===================================================================================================
class Test:

    def testModuleFinder(self):
        m = ModuleFinder()

        # Basic test
        module_name = m.ModuleName(
            'x:/coilib50/source/python/coilib50/something/file.py',
            ['x:.coilib50.source.python']
        )
        assert module_name == 'coilib50.something.file'

        # Test main
        module_name = m.ModuleName(
            'x:/coilib50/source/python/main.py',
            ['x:.coilib50.source.python']
        )
        assert module_name == 'main'

        # Test with other stuff in path
        module_name = m.ModuleName(
            'x:/coilib50/source/python/coilib50/something/file.py',
            ['x:.coilib50.source.python', 'x:.project.source.python']
        )
        assert module_name == 'coilib50.something.file'

        # Test with x:.coilib50 also in path (we should ignore paths that are not python packages)
        module_name = m.ModuleName(
            'x:/coilib50/source/python/coilib50/something/file.py',
            ['x:.coilib50', 'x:.coilib50.source.python']
        )
        assert module_name == 'coilib50.something.file'


    def testGetImports(self, embed_data):
        modules = ModuleFinder.GetImports(
            embed_data.GetDataDirectory(),
        )

        # Main shows up if we execute this test as a python script
        if '__main__' in modules:
            modules.remove('__main__')

        assert modules == [
            'ben10.foundation._tests.pytest_module_finder.module2',
            'ben10.foundation._tests.pytest_module_finder.submodule.module3',
            'os',
            'sys'
        ]
