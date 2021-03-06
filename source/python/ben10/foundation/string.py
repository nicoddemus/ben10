'''
Module for string manipulation functions
'''



#===================================================================================================
# Dedent
#===================================================================================================
def Dedent(text, ignore_first_linebreak=True, ignore_last_linebreak=True):
    '''
    Heavily inspired by textwrap.dedent, with a few changes (as of python 2.7)
        - No longer transforming all-whitespace lines into ''
        - Options to ignore first and last linebreaks of `text`.

    The last option is particularly useful because of ESSS coding standards.
    For example, using the default textwrap.dedent to create a 3-line string would look like this:
        textwrap.dedent("""    line1
            line2
            line3"""
        )

    With these options, you can create a better looking code with:
        Dedent(
            """
            line1
            line2
            line3
            """
        )

    :param str text:
        Text to be dedented (see examples above)

    :param bool ignore_first_linebreak:
        If True, everything up to the first '\n' is ignored

    :param bool ignore_last_linebreak:
        If True, everything after the last '\n' is ignored


    Original docs:
        Remove any common leading whitespace from every line in `text`.

        This can be used to make triple-quoted strings line up with the left edge of the display,
        while still presenting them in the source code in indented form.

        Note that tabs and spaces are both treated as whitespace, but they are not equal: the lines
        "  hello" and "\thello" are  considered to have no common leading whitespace.  (This
        behaviour is new in Python 2.5; older versions of this module incorrectly expanded tabs
        before searching for common leading whitespace.)
    '''
    if ignore_first_linebreak:
        text = text.split('\n', 1)[1]
    if ignore_last_linebreak:
        text = text.rsplit('\n', 1)[0]

    import re
    _leading_whitespace_re = re.compile('(^[ \t]*)(?:[^ \t\n])', re.MULTILINE)

    # Look for the longest leading string of spaces and tabs common to
    # all non-empty lines.
    margin = None
    indents = _leading_whitespace_re.findall(text)
    for indent in indents:
        if margin is None:
            margin = indent

        # Current line more deeply indented than previous winner:
        # no change (previous winner is still on top).
        elif indent.startswith(margin):
            pass

        # Current line consistent with and no deeper than previous winner:
        # it's the new winner.
        elif margin.startswith(indent):
            margin = indent

        # Current line and previous winner have no common whitespace:
        # there is no margin.
        else:
            # TODO: BEN-18: Improve coverage
            margin = ""
            break

    if margin:
        text = re.sub(r'(?m)^' + margin, '', text)
    return text



#===================================================================================================
# Indent
#===================================================================================================
def Indent(text, indent=1, indentation='    '):
    '''
    Indents multiple lines of text.

    :param list(str)|str text:
        The text to apply the indentation.

    :param int indent:
        Number of indentations to add. Defaults to 1.

    :param str indentation:
        The text used as indentation. Defaults to 4 spaces.

    :return str:
        Returns the text with applied indentation.
    '''
    indentation = indent * indentation

    lines = text
    if isinstance(lines, str):
        append_eol = lines.endswith('\n')
        lines = lines.splitlines()
    else:
        append_eol = True

    result = []
    for i in lines:
        if i.strip():
            result.append(indentation + i)
        else:
            result.append(i)
    if result:
        result = '\n'.join(result)
        if append_eol:
            result += '\n'
    else:
        result = ''
    return result



#===================================================================================================
# SafeSplit
#===================================================================================================
def SafeSplit(s, sep, maxsplit=None, default=''):
    '''
    Perform a string split granting the size of the resulting list.

    :param str s: The input string.
    :param str sep: The separator.
    :param int maxsplit: The max number of splits. The len of the resulting len is granted to be maxsplit + 1
    :param default: The default value for filled values in the result.

    :return list(str):
        Returns a list with fixed size of maxsplit + 1.
    '''
    if maxsplit is None:
        result = s.split(sep)
    else:
        result = s.split(sep, maxsplit)
        result_len = maxsplit + 1
        diff_len = result_len - len(result)
        if diff_len > 0:
            result += [default] * diff_len
    return result
