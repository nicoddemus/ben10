from etk11.refactor import TerraForming
import difflib
import inspect



#===================================================================================================
# Test
#===================================================================================================
class Test:

    def _TestLines(self, doc, processor):

        def Fail(obtained, expected):
            diff = [i for i in difflib.context_diff(obtained, expected)]
            diff = '\n'.join(diff)
            raise AssertionError(diff)

        lines = doc.split('\n')
        input_ = []
        expected = []
        stage = 'input'
        for i_line in lines:
            if i_line.strip() == '---':
                stage = 'output'
                continue
            if i_line.strip() == '===':
                obtained = processor(input_)
                if obtained != expected:
                    Fail(obtained, expected)
                input_ = []
                expected = []
                stage = 'input'
                continue

            if stage == 'input':
                input_.append(i_line)
            else:
                expected.append(i_line)

        obtained = processor(input_)
        if obtained != expected:
            Fail(obtained, expected)


    def testExtractImportLinesFromLines(self):
        '''
        import alpha, \
            bravo
        import (
            charlie,
            echo
        )
        import coilib50
        import coilib60
        import coilib70


        def Main():
        ---
        ### lineno: 0
        ### indent: 0
        import alpha, bravo
        import (charlie, echo)
        import coilib50
        import coilib60
        import coilib70
        ===
        import alpha
        ---
        ### lineno: 0
        ### indent: 0
        import alpha
        ===
        """
        This is a document string
        """
        import alpha

        def Main():
        ---
        ### lineno: 3
        ### indent: 0
        import alpha
        ===
        \'\'\'
        This is a document string
        \'\'\'
        import alpha

        def Main():
        ---
        ### lineno: 3
        ### indent: 0
        import alpha
        ===
        # This is a comment
        import alpha

        def Main():
        ---
        ### lineno: 1
        ### indent: 0
        import alpha
        ===
        from coilib50.basic._import_module import ImportModule
        ---
        ### lineno: 0
        ### indent: 0
        from coilib50.basic._import_module import ImportModule
        '''

        terra = TerraForming()

        def Doit(lines):
            result = []
            for i_lineno, (i_import_lines, _, i_indent) in terra.ExtractImportLinesFromLines(lines).iteritems():
                result.append('### lineno: %d' % i_lineno)
                result.append('### indent: %d' % i_indent)
                result += i_import_lines

            return result

        self._TestLines(inspect.getdoc(self.testExtractImportLinesFromLines), Doit)


    def testExtractImportSymbolsFromLines(self):
        '''
        import alpha, \
            bravo
        import ( charlie,
            delta
        )
        from echo import foxtrot
        import yankee # Comment
        import zulu
        
        def Main():
        ---
        ### lineno: 0
        ('from', 'echo.foxtrot', '')
        ('import', 'alpha', '')
        ('import', 'bravo', '')
        ('import', 'charlie', '')
        ('import', 'delta', '')
        ('import', 'yankee', 'Comment')
        ('import', 'zulu', '')
        ===
        import alpha
        import bravo
        
        def Main():
            import charlie
            import echo
        
        def Other():
            import yankee
            import zulu
        ---
        ### lineno: 0
        ('import', 'alpha', '')
        ('import', 'bravo', '')
        ### lineno: 4
        ('import', 'charlie', '')
        ('import', 'echo', '')
        ### lineno: 8
        ('import', 'yankee', '')
        ('import', 'zulu', '')
        ===
        import alpha

        def Main():
            """            
            A comment
            from Main
            """
        ---
        ### lineno: 0
        ('import', 'alpha', '')
        ===
        from coilib50.basic._import_module import ImportModule
        ---
        ### lineno: 0
        ('from', 'coilib50.basic._import_module.ImportModule', '')
        '''
        terra = TerraForming()

        def Doit(lines):
            result = []
            items = sorted(terra.ExtractImportSymbolsFromLines(lines).items())
            for i_lineno, (i_import_symbols, _, _) in items:
                result.append('### lineno: %d' % i_lineno)
                result += map(str, sorted(i_import_symbols))

            return result

        self._TestLines(inspect.getdoc(self.testExtractImportSymbolsFromLines), Doit)


    def testReorganizeImports(self):
        '''
        import alpha, \
            bravo
        import (
            charlie,
            delta
        )
        import coilib50
        import coilib60
        import coilib70


        def Main():
        ---
        import alpha
        import bravo
        import charlie
        import coilib50
        import coilib60
        import coilib70
        import delta



        def Main():
        ===
        from coilib50.app import command
        from etk11.foundation.decorators import Override
        from etk11.foundation.platform_ import Platform
        from sharedscripts10.namespace.namespace_types import LIST, NamespaceTypeFactory, PATH
        from sharedscripts10.shared_script import SharedScript

        # Comment
        ---
        from coilib50.app import command
        from etk11.foundation.decorators import Override
        from etk11.foundation.platform_ import Platform
        from sharedscripts10.namespace.namespace_types import LIST, NamespaceTypeFactory, PATH
        from sharedscripts10.shared_script import SharedScript



        # Comment
        ===
        from sharedscripts10.cache_service.cache_service import zulu
        from sharedscripts10.res_loader import alpha, bravo, charlie

        def Main():
        ---
        from sharedscripts10.cache_service.cache_service import zulu
        from sharedscripts10.res_loader import alpha, bravo, charlie



        def Main():
        ===
        import alpha
        ---
        import alpha
        ===
        .
        ---
        .
        ===
        """
        Comment
        """
        from ftputil import FTPHost

        #===================================================================================================
        # PermanentError
        #===================================================================================================
        try: # import for dist <= 1104
            from ftputil import PermanentError
        except: # import for dist >= 12.0
            from ftputil.ftp_error import PermanentError
        ---
        """
        Comment
        """
        from ftputil import FTPHost



        #===================================================================================================
        # PermanentError
        #===================================================================================================
        try: # import for dist <= 1104
            from ftputil import PermanentError
        except: # import for dist >= 12.0
            from ftputil.ftp_error import PermanentError
        ===
        from coilib50.basic import inter
        from coilib50.basic.inter import Interface
        from etk11.foundation.interface import Implements
        import alpha
        import bravo
        import coilib50.basic.inter
        
        def Main():
            import charlie
            import echo
        
        def Other():
            import yankee
            import zulu
        ---
        from etk11.foundation import interface
        from etk11.foundation.interface import Implements, Interface
        import alpha
        import bravo
        import etk11.foundation.interface



        def Main():
            import charlie
            import echo
        
        def Other():
            import yankee
            import zulu
        ===
        from coilib50.basic._import_module import ImportModule
        ---
        from coilib50.basic._import_module import ImportModule
        '''
        terra = TerraForming()

        def Doit(lines):
            return terra.ReorganizeImports(
                lines,
                refactor={
                    'coilib50.basic.implements': 'etk11.foundation.interface',
                    'coilib50.basic.inter': 'etk11.foundation.interface',
                }
            )

        self._TestLines(inspect.getdoc(self.testReorganizeImports), Doit)

