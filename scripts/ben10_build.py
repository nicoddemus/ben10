from aasimar10.shared_commands import BuildCommand, BuildStopped
from coilib50.basic.override import Override



#===================================================================================================
# Ben10BuildCommand
#===================================================================================================
class Ben10BuildCommand(BuildCommand):

    name = 'Ben10BuildCommand'

    @Override(BuildCommand.EvBuild)
    def EvBuild(self, args):
        from sharedscripts10.shared_scripts.python_ import Python
        _output, retcode = Python().Execute2(
            self.shared_script.Evaluate('`self.working_dir`/ci.py'),
            output_callback=self.oss.P,
            cwd=self.shared_script['working_dir']
        )
        if retcode == 999:  # Raised by ci.py when tests fail
            raise BuildStopped('Tests failed')
        elif retcode:
            raise RuntimeError('ci.py failed with retcode ' + str(retcode))

