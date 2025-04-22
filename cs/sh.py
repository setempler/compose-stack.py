# cs.sh


"""subprocess and shell handling"""


import os
import json
import shlex
import getpass
import subprocess
import asyncio
import logging
log = logging.getLogger()


from . import console


class Process(object):
    """Shell subprocess system.

    Support executing subprocesses in different variants.
    Parse output to standard objects.
    """
    def __init__(self, command=None, live=0):
        """Create and execute a subprocess."""
        if isinstance(command, str):
            command = shlex.split(command)
        if not isinstance(command, list):
            raise ValueError(f"command object not of type list: '{type(command)}'")
        self.command = command
        self.started = None
        self.obj = None
        if command is not None:
            if live:
                self.run_live(n_lines=live)
            else:
                self.run()

    def _update(self, proc):
        if isinstance(proc, subprocess.CompletedProcess):
            self.obj = proc
            log.debug(f"shell command    : {self.commandline}")
            log.debug(f"shell stdout     : {self.stdoutstripped}")
            log.debug(f"shell stderr     : {self.stderrstripped}")
            log.debug(f"shell return code: {self.code}")
    
    @property
    def commandline(self):
        """Return the text line representation of the command."""
        return " ".join(self.command)

    @property
    def is_completed(self):
        """Return `True` if subprocess was completed."""
        return isinstance(self.obj, subprocess.CompletedProcess)

    @property
    def pid(self):
        """Return the subprocess id."""
        return self.obj.pid if self.is_completed else None
        
    @property
    def code(self):
        """Return `True` if subprocess was completed."""
        return self.obj.returncode if self.is_completed else None
    
    @property
    def is_done(self):
        """Return `True` if subprocess was completed with success (returncode 0)."""
        return self.code == 0

    @property
    def stdout(self):
        """Return standard output text of subprocess."""
        if not self.is_completed:
            return None
        return self.obj.stdout

    @property
    def stdoutstripped(self):
        """Return standard error stripped text of subprocess."""
        if not self.stdout:
            return None
        return self.stdout.strip()

    @property
    def stderr(self):
        """Return standard error text of subprocess."""
        return self.obj.stderr if self.is_completed else None
    
    @property
    def stderrstripped(self):
        """Return standard error stripped text of subprocess."""
        if not self.stderr:
            return None
        return self.stderr.strip()

    @property
    def lines(self, strip=True, err=False):
        """Return stdout/stderr and parse as array of lines."""
        lines = self.stderr if err else self.stdout
        if strip:
            lines = lines.strip(os.linesep)
        return lines.split(os.linesep)

    @property
    def json(self):
        """Return standard output and parse from JSON to dict."""
        return json.loads(self.stdout.strip())

    @property
    def json_lines(self):
        """Return standard output and parse from JSON to dict."""
        lines = self.stdout.strip().split(os.linesep)
        obj = [json.loads(line) for line in lines]
        return obj

    def run(self):
        """Run a command locally."""
        proc = subprocess.run(
            " ".join(self.command),
            input = None,
            text = True,
            universal_newlines = True,
            capture_output = True,
            bufsize = 0,
            shell = True)
        self._update(proc)
        return self.is_done

    def run_extended(self, remote = None, user = None, piped = True, env = None):
        """Run a (series of) shell command(s) as user at a host.

        Wraps the `subprocess.run` method by adding features like:

        - send command as standard input to a runner, which is either
            - the local shell `bash -s` of the current user
            - the local shell using a different user with `sudo -u <user>`, or
            - the remote shell using a specified user login at a host via `ssh <user>@<host>`
        - supply environment paths exported in the shell prior to executing the command
        - return error code, stdout, stderr to a logger from the `logging` module as debug message

        Args:
            cmd (str): A string used as shell command.
            remote (str): A name of a remote server, if given ssh is invoked.
            user (str): A user name to connect with ssh to a `remote` server or
                switch to using sudo for localhost.
            piped (bool): Enable using `bash -s` to pipe commands to shell.
            env (str): Folder paths to use and export in PATH shell variable.

        Returns:
            :py:class:`subprocess.CompletedProcess`: An object holding args, returncode and stdout/stderr values
                from the executed subprocess.

        .. exec_code::
                :caption: Example code:
                :caption_output: Result:

                import miscset
                print(miscset.sh.run("uname").stdout)

        """
        cmd = self.command
        if env is None:
            env = []
        if remote in ["localhost", "127.0.0.1"]:
            remote = None
        if remote:
            runner = ["ssh"]
            if user:
                runner += [f"{user}@{remote}"]
            else:
                runner += [remote]
            if piped:
                runner += ["\"bash -s\""]
            else:
                runner += [f"\"{cmd}\""]
            if len(env):
                env = ":".join(env)
                cmd = f"export PATH=\"{env}:$PATH\"; {cmd}"
        elif user and user != getpass.getuser():
            runner = ["sudo", "-u", user]
            if piped:
                runner += ["bash -s"]
            else:
                # this case failed,
                # since sudo would not understand the string
                # "id -u -n; pwd"
                # as a command unlike ssh?
                runner += [f"\"{cmd}\""]
        else:
            if piped:
                runner = ["bash -s"]
            else:
                runner = [cmd]
        pipe_input = None
        if piped:
            pipe_input = cmd
        if remote and len(env):
            log.debug(f"shell paths are {env}")
        log.debug(f"shell stdin is {pipe_input}")
        log.debug(f"shell runner is {runner}")
        proc = subprocess.run(
            " ".join(runner),
            input = pipe_input,
            text = True,
            universal_newlines = True,
            capture_output = True,
            bufsize = 0,
            shell = True)
        self._update(proc)
        def prettify(std):
            std = std.split(os.linesep)
            std = [ line for line in std if len(line) ]
            if len(std):
                std = [""] + std
            std = os.linesep.join(std)
            return std
        return self.is_done
    
    def run_live(self, n_lines=7):
        """Run a command and live parse stdout to console."""
        # helper to parse
        async def parse_live(proc, n_lines):
            """Parse the stdout live to console."""
            prefix=f"{console.Color.dim}>> "
            delay_seconds = 1
            previous_out_line = None
            out_lines = []
            console.flush([prefix] * n_lines)
            while True:
                i = 0
                start_time = asyncio.get_event_loop().time()
                while (asyncio.get_event_loop().time() - start_time) < delay_seconds:
                    out_line = await proc.stdout.readline()
                    #err_line = await proc.stderr.readline()
                    if not out_line:# and not err_line:
                        break
                    i += 1
                    out_lines.append(out_line.decode().rstrip())
                    #out_line = f"{prefix}{out_line.decode().rstrip()}"
                if previous_out_line != out_line:
                    previous_out_line = out_line
                    print_lines = [""] * n_lines
                    last_lines = out_lines[-n_lines:]
                    print_lines[-len(last_lines):] = last_lines
                    k=len(print_lines)
                    console.replace_lines([f"{prefix}{line}{console.Color.none}" for line in print_lines])
                if i == 0:
                    break
            console.clear_lines(n_lines)
        # helper to schedule parser
        async def schedule_live(command, n_lines):
            pipe = asyncio.subprocess.PIPE
            proc = await asyncio.create_subprocess_shell(command, stdout=pipe, stderr=pipe)
            await parse_live(proc, n_lines)
            await proc.wait()
            return proc
        # execute
        proc = asyncio.run(schedule_live(self.command, n_lines))
        # store
        self._update(proc)
        return self.is_done

