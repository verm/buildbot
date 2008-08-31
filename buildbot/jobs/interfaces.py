from zope.interface import Interface, Attribute

# TODO:
# file transfers

class IRemoteCommand(Interface):
    """Represents the execution of a command on a remote system, as well as the
    results of that command.
    """

    # inputs

    remote = Attribute(
        "IRemoteSystem provider on which to execute the command")
    command = Attribute(
        "Command to run - a list of strings")
    env = Attribute(
        "Environment to execute in, or None for pre-existing")
    setEnv = Attribute(
        "Environment variables to set")
    cwd = Attribute(
        "Directory for execution or None; relative to slave instance's base")

    # state

    state = Attribute(
        "Current state of the command, one of 'new', 'running', or 'done'")

    # outputs (valid in state 'done')

    exitstatus = Attribute(
        "Command exit status (apply os.WIFEXITED etc.)")

    # TODO:
    # timeout (overall and inactivity)
    # stdin/stdout/stderr
    # logfiles + subscriptions
    # usepty
    # interrupt/kill

    def __init__(**kwargs):
        """ Create, but do not execute, an IRemoteCommand provider.  All
        parameters, specified by keyword arguments, simply set the
        corresponding attribute.  """

    def run():
        """Begin running the command remotely.  Puts the object into the
        'running' state, and returns a defererd that will fire with this object
        when the command has completed and the object is in the 'done'
        state."""

class IRemoteSystem(Interface):
    """Represents a remote system that can run commands (via IRemoteCommand).
    Constructor semantics are specific to the implementation.  """

    activeCommands = Attribute(
        "IRemoteCommands active ('new' or 'running') on this remote system")

    def newCommand(**kwargs):
        """Create a new IRemoteCommand provider linked to this system, passing
        all keyword arguments, along with remote=self, on to the IRemoteCommand
        constructor."""
