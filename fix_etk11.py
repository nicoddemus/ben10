"""Fix incompatible imports and module references."""
# Authors: Collin Winter, Nick Edds

# Local imports
from .. import fixer_base
from ..fixer_util import Name, attr_chain

MAPPING = {
    'coilib50.basic.Null' : 'etk11.null.Null', # CLASS
    'coilib50.basic._reraise' : 'etk11.reraise',
    'coilib50.basic.abstract' : 'etk11.decorators',
    'coilib50.basic.abstract' : 'etk11.decorators',
    'coilib50.basic.deprecated' : 'etk11.decorators',
    'coilib50.basic.implements' : 'etk11.interface',
    'coilib50.basic.interface' : 'etk11.interface',
    'coilib50.basic.odict' : 'etk11.odict',
    'coilib50.basic.override' : 'etk11.decorators',
    'coilib50.basic.weak_ref' : 'etk11.weak_ref',
    'coilib50.callback' : 'etk11.callback',
    'coilib50.debug' : 'etk11.debug',
    'coilib50.filesystem' : 'etk11.filesystem',
    'coilib50.path.algorithms' : 'etk11.algorithms',
    'sharedscripts10.platform_' : 'etk11.platform_',
    'coilib50.path' : 'path',
#    'etk11.cached_method.AbstractCachedMethod' : 'coilib50.cache.AbstractCachedMethod',
#    'etk11.cached_method.AttributeBasedCachedMethod' : 'coilib50.cache.AttributeBasedCachedMethod',
#    'etk11.cached_method.CachedMethod' : 'coilib50.cache.CachedMethod',
#    'etk11.cached_method.ImmutableParamsCachedMethod' : 'coilib50.cache.ImmutableParamsCachedMethod ',
#    'etk11.cached_method.LastResultCachedMethod' : 'coilib50.cache.LastResultCachedMethod',
#    'os' : 'etk11.os',
}


def alternates(members):
    return "(" + "|".join(map(repr, members)) + ")"


def build_pattern(mapping=MAPPING):

    def import_pattern(k):
        if '.' in k:
            result = "dotted_name< %s >" % " '.' ".join("'%s'" % i for i in (k.split('.')))
        else:
            result = "module_name='%s'" % k
        return result

    mod_list = ' | '.join([import_pattern(key) for key in mapping])
    bare_names = alternates(mapping.keys())

    yield """name_import=import_name< 'import' ((%s) |
               multiple_imports=dotted_as_names< any* (%s) any* >) >
          """ % (mod_list, mod_list)
    yield """import_from< 'from' (%s) 'import' ['(']
              ( any | import_as_name< any 'as' any > |
                import_as_names< any* >)  [')'] >
          """ % mod_list
    yield """import_name< 'import' (dotted_as_name< (%s) 'as' any > |
               multiple_imports=dotted_as_names<
                 any* dotted_as_name< (%s) 'as' any > any* >) >
          """ % (mod_list, mod_list)

    # Find usages of module members in code e.g. thread.foo(bar)
    yield "power< bare_with_attr=(%s) trailer<'.' any > any* >" % bare_names


class FixEtk11(fixer_base.BaseFix):

    BM_compatible = True
    keep_line_order = True
    # This is overridden in fix_imports2.
    mapping = MAPPING

    # We want to run this fixer late, so fix_import doesn't try to make stdlib
    # renames into relative imports.
    run_order = 6

    def build_pattern(self):
        return "|".join(build_pattern(self.mapping))

    def compile_pattern(self):
        # We override this, so MAPPING can be pragmatically altered and the
        # changes will be reflected in PATTERN.
        self.PATTERN = self.build_pattern()
        super(FixEtk11, self).compile_pattern()

    # Don't match the node if it's within another match.
    def match(self, node):
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

    def transform(self, node, results):
        import_mod = results.get("module_name")
        bare_name = results.get("bare_with_attr")
        node = results.get('node')

        if import_mod:
            print('OLD', import_mod)
            print('OLD', import_mod.__class__)
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
        elif bare_name:
            # Replace usage of the module.
            bare_name = bare_name[0]
            new_name = self.replace.get(bare_name.value)
            if new_name:
                bare_name.replace(Name(new_name, prefix=bare_name.prefix))
        elif node:
            import_mod = node.children[1]
            mod_name = str(import_mod).strip()
            new_name = self.mapping[mod_name]
            import_mod.replace(Name(new_name, prefix=import_mod.prefix))

