


#===================================================================================================
# ExtendedPathMask
#===================================================================================================
class ExtendedPathMask(object):
    '''
    This class is a place-holder for functions that handle the exteded path mask.

    Extended Path Mask
    ------------------
    
    The extended path mask is a file search path description used to find files based on the filename.
    This extended path mask includes the following features:
        - Recursive search (prefix with a "+" sign)
        - The possibility of adding more than one filter to match files (separated by ";")
        - The possibility of negate an mask (prefix the mask with "!"). 
    
    The extended path mask has the following syntax:
    
        [+|-]<path>/<filter>(;<filter>)*
        
    Where:
        + : recursive and copy-tree flag
        - : recursive and copy-flat flag (copy files to the target directory with no tree structure) 
        <path> : a usual path, using '/' as separator
        <filter> : A filename filter, as used in dir command:
            Ex:
                *.zip;*.rar
                units.txt;*.ini
                *.txt;!*-002.txt
    '''


    @classmethod
    def Split(cls, extended_path_mask):
        '''
        Splits the given path into their components: recursive, dirname, in_filters and out_filters 
        
        :param str: extended_path_mask:
            The "extended path mask" to split
            
        :rtype: tuple(bool,bool,str,list(str),list(str))
        :returns:
            Returns the extended path 5 components:
            - The tree-recurse flag
            - The flat-recurse flag
            - The actual path
            - A list of masks to include
            - A list of masks to exclude
        '''
        import os.path
        r_tree_recurse = extended_path_mask[0] in '+-'
        r_flat_recurse = extended_path_mask[0] in '-'

        r_dirname, r_filters = os.path.split(extended_path_mask)
        if r_tree_recurse:
            r_dirname = r_dirname[1:]

        filters = r_filters.split(';')
        r_in_filters = [i for i in filters if not i.startswith('!')]
        r_out_filters = [i[1:] for i in filters if i.startswith('!')]

        return r_tree_recurse, r_flat_recurse, r_dirname, r_in_filters, r_out_filters
