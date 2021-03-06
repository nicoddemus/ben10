from ben10.filesystem import CanonicalPath, Cwd, StandardizePath
from ben10.foundation.reraise import Reraise
from ben10.foundation.string import SafeSplit
from ben10.foundation.uname import GetExecutableDir
from cStringIO import StringIO
from txtout.txtout import TextOutput
import errno
import os
import shlex
import subprocess
import sys



#===================================================================================================
# Constants
#===================================================================================================
class COPY_FROM_ENVIRONMENT(object):
    '''
    Used as a constant for the environ dictionary value.
    See System.Execute@environ
    '''


#===================================================================================================
# PrintEnvironment
#===================================================================================================
def PrintEnvironment(environment, oss, sort_lists=True):
    '''
    Prints an environment dict into a given stream.

    :param dict(str->str) environment:
        Dictionary containing the environment
        variable_name - > value

    :param TextOutput oss:

    :param bool sort_lists:
        If True sorts the list values of environment variables.
    '''
    for i_variable_name, i_value in sorted(environment.items()):

        # Print the variable name as the header
        if sort_lists and os.pathsep in i_value:
            oss.P(i_variable_name + ' (sorted)', color='WHITE', top_margin=1)
        else:
            oss.P(i_variable_name, color='WHITE', top_margin=1)

        # Split paths to make them easier to read, if this isn't a sequence of paths, it will
        # simply be turned into a one-element list
        value_list = i_value.split(os.pathsep)

        if sort_lists:
            value_list = sorted(value_list)

        # Print all values in this variable
        for j_value in value_list:
            oss.I(j_value, indent=1)



#===================================================================================================
# EnvironmentContextManager
#===================================================================================================
class EnvironmentContextManager(object):
    '''
    Used with the 'with' statement.

    Sets the environment according to the given parameters and returns to the original environment
    once this section is over.
    '''

    def __init__(self, environ, update=False, change_sys_path=False):
        '''
        :param dict(str:str) environ:
            A dictionary of environment variables names and values

        :param bool update:
            If True only updates the current environment instead of replacing by environ.
            When exiting the update is undone and the environment is left intact.

        :param bool change_sys_path:
            If True, the sys PATH will be modified.
        '''
        self._old_environ = None
        self._old_sys_path = None

        self._new_environ = environ.copy()
        self._update = update
        self._change_sys_path = change_sys_path


    def __enter__(self):
        '''
        Copies the current environment and sets the given environment

        :param dict(str:str) environ:
            A dictionary of environment variables names and values
        '''
        self._old_environ = os.environ.copy()
        self._old_sys_path = sys.path[:]

        if not self._update:
            os.environ.clear()
            if self._change_sys_path:
                new_sys_path = sys.path[:]
                new_sys_path = map(CanonicalPath, new_sys_path)

                # Keeping python_home paths so this instance of Python continues to work.
                python_home = CanonicalPath(GetExecutableDir())
                new_sys_path = [i for i in new_sys_path if i.startswith(python_home)]

                sys.path = new_sys_path


        if self._update:
            # Merge some list variables to include new stuff
            def SetMerged(variable):
                merged_values = []

                new_value = self._new_environ.get(variable)
                if new_value is not None:
                    merged_values += new_value.split(os.pathsep)

                current_value = os.environ.get(variable)
                if current_value is not None:
                    merged_values += [
                        i for i
                        in current_value.split(os.pathsep)
                        if i not in merged_values
                    ]

                merged = os.pathsep.join(merged_values)
                if len(merged) > 0:
                    self._new_environ[variable] = merged

            SetMerged('PATH')
            SetMerged('PYTHONPATH')
            SetMerged('LD_LIBRARY_PATH')


        try:
            # Update environment variables
            os.environ.update(self._new_environ)

            if self._change_sys_path:
                sys.path += os.environ.get('PYTHONPATH', '').split(os.pathsep)

        except Exception, e:
            stream = StringIO()
            oss = TextOutput(stream)
            PrintEnvironment(self._new_environ, oss)
            Reraise(e, 'While entering an EnvironmentContextManager with:%s' % stream.getvalue())


    def __exit__(self, *args):
        '''
        Returns to the original environment.
        '''
        os.environ.clear()
        os.environ.update(self._old_environ)
        if self._change_sys_path:
            sys.path = self._old_sys_path



#===================================================================================================
# Execute
#===================================================================================================
def Execute(
        command_line,
        cwd=None,
        environ=None,
        extra_environ=None,
        input=None,  # @ReservedAssignment
        output_callback=None,
        return_code_callback=None,
        shell=False,
        ignore_auto_quote=False,
        clean_eol=True,
        pipe_stdout=True,
    ):
    '''
    Executes a shell command

    :type command_line: list(str) or str
    :param command_line:
        List of command - line to execute, including the executable as the first element in the
        list.

    :param str cwd:
        The current working directory for the execution.

    :type environ: dict(str, str)
    :param environ:
        The environment variables available for the subprocess. This will replace the current
        environment.
        If a value is "COPY_FROM_ENVIRON" the value is replaced by the current environment
        value before executing the command - line.
        This dictionary will be modified by the Execute, so make sure that this is a copy of
        your actual data, not the original.

    :param dict(str:str) extra_environ:
        Environment variables (name, value) to add to the execution environment.

    :type input: str | None
    :param input:
        Text to send as input to the process.

    :param callback(str) output_callback:
        A optional callback called with the process output as it is generated.

    :param callback(int) return_code_callback:
        A optional callback called with the execution return -code.
        The returned value is ignored.
        Because our return value is an iterator, the only way (I found) to give the user access
        to the return -code is via callback.

    :param bool shell:
        From subprocess.py:

        If shell is True, the specified command will be executed through the shell.

        On UNIX, with shell=False (default): In this case, the Popen class uses os.execvp() to
        execute the child program.  'command_line' should normally be a sequence.  A string will
        be treated as a sequence with the string as the only item (the program to execute).

        On UNIX, with shell=True: If 'command_line' is a string, it specifies the command string
        to execute through the shell.  If 'command_line' is a sequence, the first item specifies
        the command string, and any additional items will be treated as additional shell
        arguments.

    :param bool ignore_auto_quote:
        If True, passes the entire command line to subprocess as a single string, instead of
        a list of strings.

        This is useful when we want to avoid subprocess' algorithm that tries to handle quoting
        on its own when receiving a list of arguments.

        This way, we are able to use quotes as we wish, without having them escaped by subprocess.

    :param bool clean_eol:
        If True, output returned and passed to callback will be stripped of eols (\r \n)

    :param bool pipe_stdout:
        If True, pipe stdout so that it can be returned as a string and passed to the output
        callback. If False, stdout will be dumped directly to the console (preserving color),
        and the callback will not be called.

    :rtype: list(str)
    :returns:
        Returns the process execution output as a list of strings.
    '''
    def CmdLineStr(cmd_line):
        return '    ' + '\n    '.join(cmd_line)

    def EnvStr(env):
        result = ''
        for i, j in sorted(env.items()):
            if os.sep in j:
                j = '\n    * ' + '\n    * '.join(sorted(j.split(os.pathsep)))
            result += '  - %s = %s\n' % (i, j)
        return result

    # We accept strings as the command_line.
    is_string_command_line = isinstance(command_line, str)

    # Handle string/list command_list
    if ignore_auto_quote and not is_string_command_line:
        # ... with ignore_auto_quote we want a string command_line... but it came as a list
        #     NOTE: This simple join may cause problems since we can have spaces in a argument. The correct way of
        #           doing would be something like "shlex.join" (that does not exists, by the way).
        command_line = ' '.join(command_line)

    elif not ignore_auto_quote and is_string_command_line:
        # ... without ignore_auto_quote we want a list command_line... but it came as a string
        if sys.platform == 'win32':
            command, arguments = SafeSplit(command_line, ' ', 1)
            assert command.count('"') != 1, 'Command may have spaces in it. Use list instead of string.'

            # Always use normpath for command, because Windows does not like posix slashes
            command =  StandardizePath(command)
            command = os.path.normpath(command)
            command_line = [command] +  shlex.split(arguments)
        else:
            command_line = shlex.split(command_line)

    if cwd is None:
        cwd = '.'

    with Cwd(cwd):
        if environ is None:
            environ = os.environ.copy()

        if extra_environ:
            environ.update(extra_environ)

        replace_environ = {}
        for i_name, i_value in environ.iteritems():
            if i_value is COPY_FROM_ENVIRONMENT and i_name in os.environ:
                replace_environ[i_name] = os.environ[i_name]
        environ.update(replace_environ)

        try:
            with EnvironmentContextManager(environ):
                popen = subprocess.Popen(
                    command_line,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE if pipe_stdout else None,
                    stderr=subprocess.STDOUT,
                    env=environ,
                    bufsize=0,
                    shell=shell,
                )
        except Exception, e:
            Reraise(
                e,
                'While executing "System.Execute":\n'
                '  environment::\n'
                '%s\n'
                '  current working dir::\n'
                '    %s\n\n'
                '  command_line::\n'
                '%s\n'
                % (EnvStr(environ), os.getcwd(), CmdLineStr(command_line)))

        try:
            result = []
            if popen.stdin:
                if input:
                    try:
                        popen.stdin.write(input)
                    except IOError, e:
                        import errno
                        if e.errno != errno.EPIPE and e.errno != errno.EINVAL:
                            raise
                popen.stdin.close()

            if popen.stdout:
                # TODO: EDEN-245: Refactor System.Execute and derivates (git, scons, etc)
                if clean_eol:  # Read one line at the time, and remove EOLs
                    for line in iter(popen.stdout.readline, ""):
                        line = line.rstrip('\n\r')
                        if output_callback:
                            output_callback(line)
                        result.append(line)
                else:  # Read one char at a time, to keep \r and \n
                    current_line = ''
                    carriage = False
                    for char in iter(lambda: popen.stdout.read(1), ""):

                        # Check if last line was \r, if not, print what we have
                        if char != '\n' and carriage:
                            carriage = False
                            if output_callback:
                                output_callback(current_line)
                            result.append(current_line)
                            current_line = ''

                        current_line += char

                        if char == '\r':
                            carriage = True

                        if char == '\n':
                            if output_callback:
                                output_callback(current_line)
                            result.append(current_line)
                            carriage = False
                            current_line = ''

        finally:
            if popen.stdout:
                popen.stdout.close()

        popen.wait()
        if return_code_callback:
            return_code_callback(popen.returncode)

        return result



#===================================================================================================
# Execute2
#===================================================================================================
def Execute2(
        command_line,
        cwd=None,
        environ=None,
        extra_environ=None,
        output_callback=None,
        shell=False,
        ignore_auto_quote=False,
        clean_eol=True,
        pipe_stdout=True,
    ):
    '''
    Executes a shell command.

    Use the same parameters as Execute, except callback_return_code, which is overridden in
    order to return the value.

    :rtype: tuple(list(str), int)
    :returns:
        Returns a 2 - tuple with the following values
            [0]: List of string printed by the process
            [1]: The execution return code
    '''
    return_code = [None]

    def CallbackReturnCode(ret):
        return_code[0] = ret

    output = Execute(
        command_line,
        cwd=cwd,
        environ=environ,
        extra_environ=extra_environ,
        output_callback=output_callback,
        return_code_callback=CallbackReturnCode,
        shell=shell,
        ignore_auto_quote=ignore_auto_quote,
        clean_eol=clean_eol,
        pipe_stdout=pipe_stdout,
    )

    return (output, return_code[0])



#===================================================================================================
# ExecuteNoWait
#===================================================================================================
def ExecuteNoWait(command_line, cwd=None, ignore_output=False):
    '''
    Execute the given command line without waiting for the process to finish its execution.

    :return:
        Returns the resulting of subprocess.Popen.
        Use result.pid for process-id.
    '''
    with Cwd(cwd):
        try:
            if ignore_output:
                process = subprocess.Popen(
                    command_line,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
            else:
                process = subprocess.Popen(
                    command_line
                )

            return process
        except Exception, e:
            Reraise(
                e,
                'SystemSharedScript.ExecuteNoWait:\n'
                '  command_line: %s\n'
                '  cwd: %s\n'
                % (command_line, cwd))
