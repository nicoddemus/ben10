"""Fix incompatible imports and module references."""
from lib2to3 import fixer_base
from lib2to3.fixer_util import attr_chain, Name


# Local imports
MAPPING = [
    ('etk11.types_.Null', 'coilib50.basic.Null'),
    ('etk11.reraise.Reraise', 'coilib50.basic.Reraise'),
    ('etk11.callback', 'coilib50.callback'),
    ('etk11.debug', 'coilib50.debug'),
    ('etk11.decorators', 'coilib50.basic.abstract'),
    ('etk11.decorators', 'coilib50.basic.deprecated'),
    ('etk11.decorators', 'coilib50.basic.interface'),
    ('etk11.decorators', 'coilib50.basic.override'),
    ('etk11.filesystem', 'coilib50.filesystem'),
    ('etk11.filesystem', 'coilib50.path.algorithms'),
    ('etk11.interface', 'coilib50.basic.implements'),
    ('etk11.interface', 'coilib50.basic.interface'),
    ('etk11.memoize', 'coilib50.cache.memoize'),
    ('etk11.odict', 'coilib50.basic.odict'),
    ('etk11.platform_', 'sharedscripts10.platform_'),
    ('etk11.reraise', 'coilib50.basic._reraise'),
    ('etk11.weak_ref', 'coilib50.basic.weak_ref'),
    ('path', 'coilib50.path'),
]
MAPPING = dict([(j, i) for i, j in MAPPING])



#=======================================================================================================================
# FixEtk11
#=======================================================================================================================
class FixEtk11(fixer_base.BaseFix):

    BM_compatible = True
    keep_line_order = True
    mapping = MAPPING

    # We want to run this fixer late, so fix_import doesn't try to make stdlib
    # renames into relative imports.
    run_order = 6


    def build_pattern(self):

        def alternates(members):
            return "(" + "|".join(map(repr, members)) + ")"

        def dotted_name(k):
            return "dotted_name< %s >" % " '.' ".join("%r" % i for i in (k.split('.')))

        def import_pattern(k):
            if '.' in k:
                result = dotted_name(k)
            else:
                result = "module_name='%s'" % k
            return result

        def build_pattern():
            keys = self.mapping.keys()
            mod_list = ' | '.join(map(import_pattern, keys))

            # FORMAT: import MODULE
            yield """name_import=import_name< 'import' ((%(mod_list)s) | multiple_imports=dotted_as_names< any* (%(mod_list)s) any* >) >""" % locals()
            # FORMAT: from MODULE import any as any
            yield """import_from< 'from' (%(mod_list)s) 'import' ['('] ( any | import_as_name< any 'as' any > | import_as_names< any* >)  [')'] >""" % locals()
            # FORMAT: import MODULE as any
            yield """import_name< 'import' (dotted_as_name< (%(mod_list)s) 'as' any > | multiple_imports=dotted_as_names<any* dotted_as_name< (%(mod_list)s) 'as' any > any* >) >""" % locals()
            # FORMAT: MODULE.any
            bare_names = alternates(keys)
            yield "power< bare_with_attr=(%(bare_names)s) trailer<'.' any > any* >" % locals()

            # FORMAT: from MODU import LE
            for k in keys:
                if '.' not in k:
                    continue
                part_one, part_two = k.rsplit('.', 1)
                if '.' not in part_one:
                    continue
                part_one = dotted_name(part_one)
                part_two = '%r' % part_two
                r = """import_from< 'from' (part_one=%(part_one)s) 'import' ['('] ( part_two=%(part_two)s )  [')'] >""" % locals()
                yield r

#             # FORMAT: from MODULE import SYMBOL
#             keys = [i for i in self.mapping if isinstance(i, tuple)]
#             part_one = ' | '.join(set([import_pattern(i_module) for i_module, _symbol in keys]))
#             part_two = ' | '.join(set(['part_two=%r' % i_symbol for _module, i_symbol in keys]))
#
#             r = """import_from< 'from' (part_one=%(part_one)s) 'import' ['('] ( %(part_two)s )  [')'] >""" % locals()
#             print '>>>', r
#             yield r


        return "|".join(build_pattern())


    def compile_pattern(self):
        # We override this, so MAPPING can be pragmatically altered and the
        # changes will be reflected in PATTERN.
        self.PATTERN = self.build_pattern()
        super(FixEtk11, self).compile_pattern()


    def match(self, node):
        '''
        Don't match the node if it's within another match.
        '''
        match = super(FixEtk11, self).match
        results = match(node)
        if results:
            # Module usage could be in the trailer of an attribute lookup, so we
            # might have nested matches when "bare_with_attr" is present.
            if "bare_with_attr" not in results and \
                    any(match(obj) for obj in attr_chain(node, "parent")):
                return False
            return results
        return False


    def start_tree(self, tree, filename):
        super(FixEtk11, self).start_tree(tree, filename)
        self.replace = {}


    def transform_module_name(self, node, results):
        import_mod = results.get("module_name")
        mod_name = import_mod.value
        new_name = self.mapping[mod_name]
        import_mod.replace(Name(new_name, prefix=import_mod.prefix))
        if "name_import" in results:
            # If it's not a "from x import x, y" or "import x as y" import,
            # marked its usage to be replaced.
            self.replace[mod_name] = new_name
        if "multiple_imports" in results:
            # This is a nasty hack to fix multiple imports on a line (e.g.,
            # "import StringIO, urlparse"). The problem is that I can't
            # figure out an easy way to make a pattern recognize the keys of
            # MAPPING randomly sprinkled in an import statement.
            results = self.match(node)
            if results:
                self.transform(node, results)


    def transform_bare_with_attr(self, node, results):
        bare_name = results.get("bare_with_attr")
        bare_name = bare_name[0]
        new_name = self.replace.get(bare_name.value)
        if new_name:
            bare_name.replace(Name(new_name, prefix=bare_name.prefix))


    def transform_node(self, node, results):
        import_mod = node.children[1]
        mod_name = str(import_mod).strip()
        new_name = self.mapping[mod_name]
        import_mod.replace(Name(new_name, prefix=import_mod.prefix))


    def transform(self, node, results):
        if 'part_one' in results:
            part_one = results.get("part_one")
            part_two = results.get("part_two")
            mod_name = '.'.join([str(part_one).strip(), part_two.value])
            new_name = self.mapping[mod_name]
            new_one, new_two = new_name.rsplit('.', 1)
            part_one.replace(Name(new_one, prefix=part_one.prefix))
            part_two.replace(Name(new_two, prefix=part_two.prefix))
        elif 'module_name' in results:
            self.transform_module_name(node, results)
        elif 'bare_with_attr' in results:
            self.transform_bare_with_attr(node, results)
        elif 'node' in results:
            self.transform_node(node, results)

