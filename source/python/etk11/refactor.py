from etk11.foundation.filesystem import FindFiles
from etk11.foundation.reraise import Reraise
import difflib
import inspect
import re



REFACTOR = [
    ('etk11.foundation.pushpop', 'coilib50.basic.pushpop'),
    ('etk11.foundation.bunch.Bunch', 'coilib50.basic.Bunch'),
    ('etk11.foundation.types_.CheckType', 'coilib50.basic.CheckType'),
    ('etk11.foundation.callback', 'coilib50.message.callback'),
    ('etk11.foundation.debug', 'coilib50.debug'),
    ('etk11.foundation.decorators', 'coilib50.basic.abstract'),
    ('etk11.foundation.decorators', 'coilib50.basic.deprecated'),
    ('etk11.foundation.decorators', 'coilib50.basic.interface'),
    ('etk11.foundation.decorators', 'coilib50.basic.override'),
    ('etk11.foundation.filesystem', 'coilib50.filesystem'),
    ('etk11.foundation.filesystem', 'coilib50.path.algorithms'),
    ('etk11.foundation.interface', 'coilib50.basic.implements'),
    ('etk11.foundation.interface', 'coilib50.basic.interface'),
    ('etk11.foundation.is_frozen.IsFrozen', 'coilib50.IsFrozen'),
    ('etk11.foundation.klass', 'coilib50.basic.klass'),
    ('etk11.foundation.memoize', 'coilib50.cache.memoize'),
    ('etk11.foundation.module_finder', 'coilib50.path.module_finder'),
    ('etk11.foundation.odict', 'coilib50.basic.odict'),
    ('etk11.foundation.platform_', 'sharedscripts10.platform_'),
    ('etk11.foundation.profiling', 'coilib50.debug.profiling'),
    ('etk11.foundation.redirect_output', 'coilib50.basic.redirect_output'),
    ('etk11.foundation.reraise', 'coilib50.basic._reraise'),
    ('etk11.foundation.reraise.Reraise', 'coilib50.basic.Reraise'),
    ('etk11.foundation.singleton', 'coilib50.basic.singleton'),
    ('etk11.foundation.types_.Flatten', 'coilib50.basic.Flatten'),
    ('etk11.foundation.types_.Null', 'coilib50.basic.Null'),
    ('etk11.foundation.types_Boolean', 'coilib50.basic.boolean.Boolean'),
    ('etk11.foundation.uname.GetApplicationDir', 'coilib50.system.GetApplicationDir'),
    ('etk11.foundation.url', 'coilib50.basic.url.url'),
    ('etk11.foundation.weak_reTf', 'coilib50.basic.weak_ref'),
    ('etk11.txtout.TextOutput', 'coilib50.io.txtout.txtout.TextOutput'),
    ('path', 'coilib50.path'),
]
REFACTOR = dict([(j, i) for i, j in REFACTOR])



#===================================================================================================
# TerraForming
#===================================================================================================
class TerraForming():

    def ReorganizeImportsInFile(self, filename, refactor={}):
        try:
            lines = [i.rstrip('\n') for i in open(filename, 'r').readlines()]
            lines = self.ReorganizeImports(lines, refactor=refactor)
            content = '\n'.join(lines)
            if lines:
                content += '\n'
            open(filename, 'wb').write(content)
        except Exception, e:
            Reraise(e, "While processing file: %s" % filename)



    def ReorganizeImports(self, lines, refactor={}):
        isgroups = self.ExtractImportSymbolsFromLines(lines)

        import_header = True
        done = 0
        r_lines = []
        lines_to_delete = []
        for i_lineno, i_line in enumerate(lines):
            if i_lineno in isgroups:
                done = 0
                import_symbols, lines_to_delete, indent = isgroups[i_lineno]

            if i_lineno in lines_to_delete:
                if done == 0:
                    r_lines += self.FormatImports(import_symbols, indent=indent, refactor=refactor)
                    done += 1
                continue

            if i_line.strip() and done == 1:
                if import_header:
                    r_lines += [''] * 3
                    import_header = False
                done += 1

            r_lines.append(i_line)

        return r_lines


    # Input: Methods related to extracting import-symbols.


    def ExtractImportSymbolsFromLines(self, lines):
        import_lines_groups = self.ExtractImportLinesFromLines(lines)
        result = {}
        for i_key, (i_import_lines, i_lines_to_delete, i_indent) in import_lines_groups.iteritems():
            import_symbols = set()
            for j_import_line in i_import_lines:
                import_symbols.update(set(self.ExtractImportSymbolsFromImportLine(j_import_line)))
            result[i_key] = (import_symbols, i_lines_to_delete, i_indent)
        return result


    def ExtractImportLinesFromLines(self, lines):

        class Context:

            CONTEXT_SKIP = 0
            CONTEXT_IMPORT = 1
            CONTEXT_MSTRING = 2

            def __init__(self):
                self.Reset()

            def Reset(self):
                self.context = self.CONTEXT_SKIP
                self.lineno = None
                self.import_lines = []
                self.lines_to_delete = []
                self.indent = 0

        context = Context()


        def IsImportLine(line):
            result = line.lstrip().startswith('import ') or line.lstrip().startswith('from ')
            if result:
                r_indent = len(line) - len(line.lstrip())
                return True, r_indent
            return False, None


        def Done(context):
            result[context.lineno] = (context.import_lines, context.lines_to_delete, context.indent)
            context.Reset()

        result = {}
        import_line = ''
        for i, i_line in enumerate(lines):

            # Skip multi-line strings.
            if '"""' in i_line or "'''" in i_line:
                if context.context == context.CONTEXT_MSTRING:
                    context.context = context.CONTEXT_SKIP
                else:
                    context.context = context.CONTEXT_MSTRING
                continue

            if context.context == context.CONTEXT_MSTRING:
                continue

            is_import_line, indent = IsImportLine(i_line)
            if indent is not None:
                context.indent = indent

            if context.context == context.CONTEXT_SKIP:
                # Switch to CONTEXT_IMPORT
                if is_import_line:
                    context.context = context.CONTEXT_IMPORT
                    context.lineno = i
                else:
                    continue  # Skipping non-import lines

            # Skip all comments
            if i_line.strip().startswith('#'):
                Done(context)

            # Skip empty lines, but considers them as part of import header
            if i_line.strip() == '':
                # ... but only import header, not inline imports.
                if len(result) == 0:
                    context.lines_to_delete.append(i)
                continue

            if is_import_line or import_line:
                context.lines_to_delete.append(i)

                # Multi-line imports with parentesis
                if '(' in import_line or '(' in i_line:
                    import_line += i_line.strip()  # <-- Content is added to line
                    if import_line.endswith(','):
                        import_line += ' '
                    if ')' not in import_line:
                        continue

                # Multi-line imports with backslash
                elif i_line.endswith('\\'):
                    import_line += i_line.lstrip().rstrip('\\')  # <-- Content is added to line
                    continue
                else:
                    import_line += i_line.lstrip()  # <-- Content is added to line
                import_line = import_line.rstrip('\n')
                import_line, _count = re.subn('  +', ' ', import_line)
                context.import_lines.append(import_line)
                import_line = ''
                continue

            Done(context)

        if context.lineno is not None:
            Done(context)

        return result


    def ExtractImportSymbolsFromImportLine(self, import_line):
        try:
            work_line, comment = import_line.split('#', 1)
            comment = comment.lstrip()
        except ValueError:
            work_line = import_line
            comment = ''

        work_line = work_line.strip(' \n')
        work_line = work_line.replace('(', '')
        work_line = work_line.replace(')', '')

        if work_line.startswith('from '):
            import_mode = 'from'
            work_line = work_line[len(import_mode):].strip()
            try:
                module, symbols = work_line.split(' import ', 1)
            except Exception, e:
                Reraise(e, 'While splitting import_line: "%s"' % import_line)
        else:
            import_mode = 'import'
            module = ''
            symbols = work_line[len(import_mode):].strip()

        if module:
            module += '.'

        symbols = [(import_mode, module + i.strip(), comment) for i in symbols.split(',') if i]
        return symbols


    # Output: methods related with the generation of data based on import-symbols

    def FormatImports(self, import_symbols, indent=0, refactor={}):

        def GetRefactor(import_symbol):
            result = refactor.get(import_symbol)
            if result is not None:
                return result

            try:
                module, symbol = import_symbol.rsplit('.', 1)
            except ValueError:
                return import_symbol
            else:
                result = refactor.get(module)
                if result is not None:
                    return result + '.' + symbol

            return import_symbol

        result = []
        import_imports = []
        from_imports = {}
        for i_import_mode, i_import_symbol, _comment in import_symbols:

            import_symbol = GetRefactor(i_import_symbol)

            if i_import_mode == 'import':
                import_imports.append(import_symbol)
            elif i_import_mode == 'from':
                module, symbol = import_symbol.rsplit('.', 1)
                from_imports.setdefault(module, []).append(symbol)
            else:
                raise RuntimeError('Unknown import-mode: %s' % i_import_mode)

        for i_module, i_symbols in sorted(from_imports.iteritems()):
            r = '%sfrom %s import %s' % (' ' * indent, i_module, ', '.join(sorted(i_symbols)))
            result.append(r)

        for i_import in sorted(import_imports):
            r = '%simport %s' % (' ' * indent, i_import)
            result.append(r)

        return result



#=======================================================================================================================
# Test
#=======================================================================================================================
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



#===================================================================================================
# Entry Point
#===================================================================================================
if __name__ == '__main__':
    import os
    import sys

    try:
        path = sys.argv[0]
    except IndexError:
        path = '.'

    if os.path.isdir(path):
        filenames = FindFiles(path, ['*.py'])
    else:
        filenames = [path]

    for i_filename in filenames:
        terra = TerraForming()
        terra.ReorganizeImportsInFile(i_filename, refactor=REFACTOR)
