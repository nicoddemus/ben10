from ben10.module_finder import ModuleFinder
import pytest



pytest_plugins = ["ben10.fixtures"]


#===================================================================================================
# Test
#===================================================================================================
class Test:

    def testModuleFinder(self):
        m = ModuleFinder()

        # Basic test
        module_name = m.ModuleName(
            'x:/ben10/source/python/ben10/something/file.py',
            ['x:.ben10.source.python']
        )
        assert module_name == 'ben10.something.file'

        # Test main
        module_name = m.ModuleName(
            'x:/ben10/source/python/main.py',
            ['x:.ben10.source.python']
        )
        assert module_name == 'main'

        # Test with other stuff in path
        module_name = m.ModuleName(
            'x:/ben10/source/python/ben10/something/file.py',
            ['x:.ben10.source.python', 'x:.project.source.python']
        )
        assert module_name == 'ben10.something.file'

        # Test with x:.ben10 also in path (we should ignore paths that are not python packages)
        module_name = m.ModuleName(
            'x:/ben10/source/python/ben10/something/file.py',
            ['x:.ben10', 'x:.ben10.source.python']
        )
        assert module_name == 'ben10.something.file'

        m = ModuleFinder(python_path='/home/alpha;/home/bravo')
        assert m.ModuleName('/home/alpha/file.py') == 'file'

        with pytest.raises(RuntimeError):
            module_name = m.ModuleName(
                'x:/alpha/python/file.py',
                ['x:.ben10.source.python']
            )


    def testGetImports(self, embed_data):
        modules = ModuleFinder.GetImports(
            embed_data.GetDataDirectory(),
        )

        # Main shows up if we execute this test as a python script
        if '__main__' in modules:
            modules.remove('__main__')

        assert modules == [
            'ben10._tests.pytest_module_finder.module2',
            'ben10._tests.pytest_module_finder.submodule.module3',
            'os',
            'sys'
        ]


    def testSystemPath(self):
        m_finder = ModuleFinder(python_path='/home/python/path;x:/project10/source/python')
        assert m_finder.SystemPath() == [
            '.home.python.path',
            'x:.project10.source.python'
            ]
        assert m_finder.SystemPath(directories=['x:/other10/source/python']) == [
            '.home.python.path',
            'x:.project10.source.python'
            ]

        m_finder = ModuleFinder(
            extend_sys_path=True,
            python_path='/home/python/path;x:/project10/source/python'
        )
        assert m_finder.SystemPath(directories=['x:/other10/source/python']) == [
            'x:.other10.source.python',
            '.home.python.path',
            'x:.project10.source.python',
            ]
