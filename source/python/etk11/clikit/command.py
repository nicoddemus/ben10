from .console import BufferedConsole
from collections import OrderedDict
import pytest
import re



#====================================================================================================
# IsString
#====================================================================================================
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

    class Arg:
        '''
        Holds meta-information about the associated function argument.
        
        I'm using this meta class because it is easier to handle it than trying to figure out the attributes inside @argparse@ to print help message.
        '''
        def __init__(self, name, default=None):
            self.name = name
            self.default = default
            self.description = '(no description)'

        def __str__(self):
            if self.default in (None, True, False):
                return self.name
            else:
                return '%s=%s' % (self.name, self.default)

        def ConfigureArgumentParser(self, parser):
            '''
            Configures the given parser with an argument matching the information in this class.
            
            :param parser: argparse.ArgumentParser
            '''
            if self.default is None:
                parser.add_argument(self.name)
            elif self.default is True:
                parser.add_argument('--%s' % self.name, action='store_true')
            elif self.default is False:
                parser.add_argument('--%s' % self.name, action='store_false')
            else:
                parser.add_argument('--%s' % self.name, default=self.default)


    def __init__(self, func, names=None):
        self.func = func
        if names is None:
            self.names = [func.__name__]  # default to function name
        elif IsString(names):
            self.names = [names]  # a single name
        else:
            self.names = names  # already a list

        # Meta-info from function inspection
        args, self.trail, self.kwargs, defaults = self._ParseFunctionArguments(self.func)

        # Holds the names of args that request fixtures.
        self.fixtures = []

        # Holds a dict, mapping the arg name to an Arg instance. (See Arg class)
        self.args = OrderedDict()

        first_default = len(args) - len(defaults)
        for i, i_arg in enumerate(args):
            if i_arg.endswith('_'):
                self.fixtures.append(i_arg)
                continue
            if i < first_default:
                self.args[i_arg] = self.Arg(i_arg)
            else:
                self.args[i_arg] = self.Arg(i_arg, defaults[i - first_default])

        # Meta-info from
        description, arg_descriptions = self._ParseDocString(self.func.__doc__ or '')
        self.description = description or '(no description)'
        for i_arg, i_description in arg_descriptions.iteritems():
            self.args[i_arg].description = i_description


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
        positionals = [i for i in self.args.values() if i.default is None]
        optionals = [i for i in self.args.values() if i.default is not None]
        console.Print('%s %s %s' % (
            ','.join(self.names),
            ','.join(['<%s>' % i for i in positionals]),
            ','.join(['[--%s]' % i for i in optionals]),
        ), indent=1, newlines=2)
        console.Print('Parameters:')
        for i in positionals:
            console.Print('%s   %s' % (i.name, i.description), indent=1)
        console.Print()
        console.Print('Options:')
        for i in optionals:
            if i.default in (True, False):
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
        '''
        kwargs = {}

        # Fixtures
        try:
            kwargs.update(dict(
                [(i, fixtures[i]) for i in self.fixtures]
            ))
        except KeyError as exception:
            raise InvalidFixture(str(exception))

        # Default values
        kwargs.update(dict([(i.name, i.default) for i in self.args.values() if i.default is not None]))

        # Passed arguments (argd)
        kwargs.update(dict([i for i in argd.iteritems() if i[0] in self.args]))

        return self.func(**kwargs)
