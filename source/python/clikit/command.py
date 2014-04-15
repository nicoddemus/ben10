from .console import BufferedConsole
from collections import OrderedDict
import re



#===================================================================================================
# IsString
#===================================================================================================
def IsString(variable):
    '''
    PLACEHOLD to check if this given variable is a string in a PYTHON 3 safe way.
    '''
    return isinstance(variable, str)



#===================================================================================================
# InvalidFixture
#===================================================================================================
class InvalidFixture(KeyError):
    '''
    Exception raised when an unknown argument is added to a command-function.
    '''
    pass


#===================================================================================================
# MissingArgument
#===================================================================================================
class MissingArgument(KeyError):
    '''
    Exception raised when an unknown argument is added to a command-function.
    '''
    pass



#===================================================================================================
# Command
#===================================================================================================
class Command:
    '''
    Holds the information for a command, directly associated with a function that implements it.
    '''

    class DEFAULT(object):
        '''
        Placeholder for posititional arguments with default value.

        Usage:

            def Hello(self, console_, p1=DEFAULT('default'):
                console_.Print(p1)

            >hello
            default
            >hello other
            other
        '''


        def __init__(self, default):
            '''
            :param object default:
                The default value for the positional argument.
            '''
            self.default = default


        def CreateArg(self, name):
            '''
            Creates Arg instance for our positional with default argument.

            :param str name:
                The name of the argument.
            '''
            return Command.Arg(name, Command.Arg.ARG_TYPE_POSITIONAL, self.default)


    class Arg:
        '''
        Holds meta-information about the associated *function parameter*.
        '''
        NO_DEFAULT = object()

        ARG_TYPE_POSITIONAL = 'P'
        ARG_TYPE_OPTION = "O"
        ARG_TYPE_FIXTURE = "F"
        ARG_TYPE_TRAIL = "T"

        def __init__(self, name, arg_type, default=NO_DEFAULT):
            '''
            :param str name:
                The argument name.
            :param ARG_TYPE_XXX arg_type:
                The type of the argument in CliKit scope.
                See ARG_TYPE_XXX constants.
            :param object default:
                The default value for this argument.
            '''
            self.name = name
            self.arg_type = arg_type
            self.default = default
            self.description = '(no description)'


        def __str__(self):
            if self.arg_type == self.ARG_TYPE_TRAIL:
                return '*' + self.name
            elif any(map(lambda x: self.default is x, (Command.Arg.NO_DEFAULT, True, False))):
                return self.name
            elif self.default is None:
                return '%s=VALUE' % self.name
            else:
                return '%s=%s' % (self.name, self.default)


        def __repr__(self):
            '''
            Representation for debug purposes.
            '''
            return '<Arg %s>' % self.__str__()


        def ConfigureArgumentParser(self, parser):
            '''
            Configures the given parser with an argument matching the information in this class.

            :param parser: argparse.ArgumentParser
            '''
            if self.arg_type == self.ARG_TYPE_FIXTURE:
                pass
            elif self.arg_type == self.ARG_TYPE_TRAIL:
                parser.add_argument(self.name, nargs='+')
            elif self.arg_type == self.ARG_TYPE_OPTION:
                if self.default is True:
                    parser.add_argument('--%s' % self.name, action='store_true')
                elif self.default is False:
                    parser.add_argument('--%s' % self.name, action='store_false')
                else:
                    parser.add_argument('--%s' % self.name, default=self.default)
            elif self.arg_type is self.ARG_TYPE_POSITIONAL:
                if self.default is self.NO_DEFAULT:
                    parser.add_argument(self.name)
                else:
                    parser.add_argument(self.name, nargs='?', default=self.default)
            else:
                raise TypeError('Unknown arg_type==%r' % self.arg_type)


    def __init__(self, func, names=None):
        '''
        :param <function> func:
            A function to wrap as a command.

        :param None|str|list(str) names:
            A list of names for the command.
            By default uses the function name converted to "command style".
            If not None, uses only the names from this argument, ignoring the function name.
        '''
        self.func = func
        if names is None:
            self.names = [func.__name__]  # default to function name
        elif IsString(names):
            self.names = [names]  # a single name
        else:
            self.names = names  # already a list

        # Meta-info from function inspection
        args, trail, self.kwargs, defaults = self._ParseFunctionArguments(self.func)

        # Holds a dict, mapping the arg name to an Arg instance. (See Arg class)
        self.args = OrderedDict()

        first_default = len(args) - len(defaults)
        for i, i_arg in enumerate(args):
            if i_arg.endswith('_'):
                self.args[i_arg] = self.Arg(i_arg, self.Arg.ARG_TYPE_FIXTURE)
            elif i < first_default:
                self.args[i_arg] = self.Arg(i_arg, self.Arg.ARG_TYPE_POSITIONAL)
            else:
                default = defaults[i - first_default]
                if isinstance(default, Command.DEFAULT):
                    self.args[i_arg] = default.CreateArg(i_arg)
                else:
                    self.args[i_arg] = self.Arg(i_arg, self.Arg.ARG_TYPE_OPTION, default)

        # Adds trail (*args) to the list of arguments.
        # - Note that these arguments have a asterisk prefix.
        if trail is not None:
            self.args[trail] = self.Arg(trail, self.Arg.ARG_TYPE_TRAIL)

        # Meta-info from
        description, arg_descriptions = self._ParseDocString(self.func.__doc__ or '')
        self.description = description or '(no description)'
        for i_arg, i_description in arg_descriptions.iteritems():
            try:
                self.args[i_arg].description = i_description
            except KeyError, e:
                raise RuntimeError('%s: argument not found for documentation entry.' % str(e))


    def _ParseFunctionArguments(self, func):
        '''
        Parses function arguments returning meta information about it.

        :return tuple:
            [0]: args: The list with the name of all the function arguments.
            [1]: trail?
            [2]: kwargs: if the function is using it, otherwise None.
            [3]: defaults: The defaults value for the argument (if given any)
        '''
        import inspect
        args, trail, kwargs, defaults = inspect.getargspec(func)
        defaults = defaults or []
        return args, trail, kwargs, defaults


    PARAM_RE = re.compile(':param (.*):(.*)$')

    def _ParseDocString(self, docstring):
        '''
        Parses the (function) docstring for the genral and arguments descriptions.

        :param docstring: A well formed docstring of a function.
        :rtype: tuple(str, list(str))
        :returns:
            Returns the function description (doc's first line) and the description of each
            argument (sphinx doc style).
        '''
        description = None
        arg_descriptions = {}

        lines = docstring.split('\n')
        for i_line in lines:
            i_line = i_line.strip()
            if not i_line:
                continue
            if description is None and i_line:
                description = i_line
                continue
            m = self.PARAM_RE.match(i_line)
            if m:
                arg, doc = m.groups()
                arg_descriptions[arg.strip()] = doc.strip()

        return description or '', arg_descriptions


    def FormatHelp(self):
        '''
        Format help for this command.

        :return str:
        '''
        console = BufferedConsole()
        console.Print('Usage:')
        positionals = [i for i in self.args.values() if i.arg_type in (self.Arg.ARG_TYPE_POSITIONAL, self.Arg.ARG_TYPE_TRAIL)]
        optionals = [i for i in self.args.values() if i.arg_type == self.Arg.ARG_TYPE_OPTION]
        console.Print('%s %s %s' % (
            ','.join(self.names),
            ' '.join(['<%s>' % i for i in positionals]),
            ','.join(['[--%s]' % i for i in optionals]),
        ), indent=1, newlines=2)
        console.Print('Parameters:')
        for i in positionals:
            console.Print('<teal>%s</>   %s' % (i.name, i.description), indent=1)
        console.Print()
        console.Print('Options:')
        for i in optionals:
            if any(map(lambda x: i.default is x, (Command.Arg.NO_DEFAULT, None, True, False))):
                console.Print('--%s   %s' % (i.name, i.description), indent=1)
            else:
                console.Print('--%s   %s [default: %s]' % (i.name, i.description, i.default), indent=1)
        return console.GetOutput()


    def ConfigureArgumentParser(self, parser):
        '''
        Configures the given parser with all arguments of this command.

        :param parser: argparse.ArgumentParser
        '''
        for i_arg in self.args.itervalues():
            i_arg.ConfigureArgumentParser(parser)


    def Call(self, fixtures, argd):
        '''
        Executes the function filling the fixtures and options parameters.

        :param fixtures:
            Map of fixtures to pass to the function as requested.

        :param argd:
            Map of option values as passed by the user in the command line.

        :return:
            Returns the command function result.
        '''
        args = []
        for i_arg in self.args.itervalues():
            if i_arg.arg_type == i_arg.ARG_TYPE_FIXTURE:
                try:
                    arg = fixtures[i_arg.name]
                except KeyError as exception:
                    raise InvalidFixture(str(exception))
                args.append(arg)
            elif i_arg.arg_type == i_arg.ARG_TYPE_TRAIL:
                args += argd.get(i_arg.name, ())
            elif i_arg.arg_type == i_arg.ARG_TYPE_POSITIONAL:
                arg = argd.get(i_arg.name, i_arg.default)
                if arg is self.Arg.NO_DEFAULT:
                    raise TypeError(i_arg.name)
                else:
                    args.append(arg)
            elif i_arg.arg_type == i_arg.ARG_TYPE_OPTION:
                arg = argd.get(i_arg.name, i_arg.default)
                args.append(arg)

        return self.func(*args)


    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
