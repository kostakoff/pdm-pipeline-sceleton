"""Shell-command runner."""

import select
import shlex
import subprocess
from dataclasses import dataclass
from typing import List, Union

from src import logger


class _Command:
    """Command class.

    Contains preformatted command in shell and exec formats .
    """

    def __init__(self, cmd: Union[str, List[str]]):
        self._cmd = cmd

    @property
    def shellf(self) -> str:  # sourcery skip: assign-if-exp, reintroduce-else
        """Shell-format command .

        Returns:
            str: command
        """
        if isinstance(self._cmd, list):
            # NOTE: не работает на python 3.6
            # return shlex.join(self._cmd)
            return " ".join(self._cmd)
        return self._cmd

    @property
    def execf(
        self,
    ) -> List[str]:  # sourcery skip: assign-if-exp, reintroduce-else
        """Exec-format command .

        Returns:
            list[str]: command
        """
        if isinstance(self._cmd, str):
            return shlex.split(self._cmd)
        return self._cmd


@dataclass
class _CallAnswer:
    returncode: int
    stdout: str


@dataclass
class CmdExecutorAnswer:
    """Dataclass contains runned command result."""

    exit_code: int
    command: _Command
    stdout: str = ""
    stderr: str = ""


@dataclass
class CmdExecutorParallelAnswer:
    """Dataclass contains subprocess pid and result of it execution."""

    pid: int
    result: CmdExecutorAnswer


class CmdExecutorAnswerResultError(Exception):
    """Execution of command ends with error."""

    def __init__(self, answer: CmdExecutorAnswer):
        """Exception constructor.

        Args:
            answer (CmdExecutorAnswer): result of command execution.
        """
        self.exit_code = answer.exit_code
        self.command = answer.command
        self.stderr = answer.stderr
        self.stdout = answer.stdout
        self.answer = answer

    def __str__(self):
        """Exception message."""
        return (
            f"Command: {self.command.execf}"
            f" Exitcode: {self.exit_code}"
            f" STDERR: {self.stderr}"
        )


class CmdExecutor:
    """Shell command runner ."""

    @staticmethod
    def _prepare_command(cmd: Union[str, List[str]]) -> _Command:
        """Parse raw command into exec and shell formats.

        Args:
            cmd (Union[str, List[str]]): Raw command

        Raises:
            ValueError: Empty string or empty List[str]

        Returns:
            _Command: Object with parsed commands.
        """
        if not cmd:
            raise ValueError("Empty command")
        return _Command(cmd)

    @staticmethod
    def _call(
        cmd: _Command,
        call_log: bool,
    ) -> _CallAnswer:  # sourcery skip: use-named-expression
        """Call mode for subprocess .

        With this mode runned process will print output line by line in live mode, while it works.

        Args:
            cmd (str): Command to run

        Returns:
            _CallAnswer: Exit code and full output as variable 'out'
        """
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True,
            bufsize=1
        )

        out = ""

        while proc.returncode is None:
            ready_to_read, _, _ = select.select([proc.stdout], [], [], 0.1)
            if ready_to_read:
                out_line = proc.stdout.readline()
                if out_line:
                    out += out_line
                    if call_log:
                        logger.info(out_line.replace('\n', ''))

            proc.poll()

        remaining_output = proc.stdout.read()
        if remaining_output:
            out += remaining_output
            if call_log:
                logger.info(remaining_output)

        return _CallAnswer(returncode=proc.returncode, stdout=out)

    @staticmethod
    def _prepare_check_result_answer(
        answer: CmdExecutorAnswer, hidden_command: bool = False
    ) -> CmdExecutorAnswer:
        """Prepare answer for check result method.

        Args:
            answer (CmdExecutorAnswer): Result of command execution.
            hidden_command (bool, optional): Hides command attribute in answer.
                Defaults to False.

        Returns:
            CmdExecutorAnswer: Result of command execution.
        """
        if hidden_command:
            answer = CmdExecutorAnswer(
                exit_code=answer.exit_code,
                command=_Command(["HIDDEN"]),
                stdout=answer.stdout,
                stderr=answer.stdout,
            )
        return answer

    @staticmethod
    def _invoke_call(cmd: _Command, call_log: bool) -> CmdExecutorAnswer:
        """Invoke call command run.

        Args:
            cmd (_Command): Command to execute.

        Returns:
            CmdExecutorAnswer: Result of command execution.
        """
        logger.info("Call mode.")
        result = CmdExecutor._call(cmd.shellf, call_log)
        return CmdExecutorAnswer(result.returncode, cmd, result.stdout)

    @staticmethod
    def _invoke_run(
        cmd: _Command, stdin: Union[str, None]
    ) -> CmdExecutorAnswer:
        """Invoke normal command run.

        Args:
            cmd (_Command): Command to execute.
            stdin (Union[str, None]): Stdin for process.

        Returns:
            CmdExecutorAnswer: Result of command execution.
        """
        logger.info("Normal mode.")
        result = subprocess.run(
            cmd.execf,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            input=stdin,
            universal_newlines=True,
        )
        return CmdExecutorAnswer(
            result.returncode, cmd, result.stdout, result.stderr
        )

    @staticmethod
    def check_result(answer: CmdExecutorAnswer) -> None:
        """Check result of command execution.

        Args:
            answer (CmdExecutorAnswer): result of command execution.

        Raises:
            CmdExecutorAnwerResultError: if command was end with errorcode.
        """
        logger.debug(f"answer: {answer.__dict__}")
        logger.debug(f"answer.command: {answer.command.__dict__}")

        if answer.exit_code:
            raise CmdExecutorAnswerResultError(answer)

    @staticmethod
    def run_cmd(
        cmd: Union[str, List[str]],
        stdin: Union[str, None] = None,
        call: bool = False,
        hidden_command: bool = False,
        check_result: bool = False,
        call_log: bool = True,
    ) -> CmdExecutorAnswer:
        """Run a command as subprocess and returns a CmdExecutorAnswer.

        Args:
            command (str, list[str]): Command in cmd format ["run", "my", "command"]
            call (bool, optional): Call mode for subprocess.
                With this mode runned process will print output line by line
                in live mode, while it works. Defaults to False.
            hidden_command(bool, optional): Hide info log with command to run.
            stdin (str, list[str]): Input for command run, often uses for pipe '|' commands.
            check_result (bool, optional): invoke CmdExecutor.check_result(<T>CmdExecutorAnswer). Defaults to False.
            call_log (bool, optional): Call mode, can turn off or on print output line by line.  Defaults to True.
        Raises:
            ValueError: Empty command
            CmdExecutorAnwerResultError: CmdExecutor have errors while try run command

        Returns:
            CmdExecutorAnswer: Result of command exec object
                contains attrs(exit_code, command, stdout, stderr)
        """
        command = CmdExecutor._prepare_command(cmd)

        try:
            if not hidden_command:
                logger.info(f"Run command: {command.execf}.")

            if call:
                answer = CmdExecutor._invoke_call(command, call_log)
            else:
                answer = CmdExecutor._invoke_run(command, stdin)

            if check_result:
                answer = CmdExecutor._prepare_check_result_answer(
                    answer, hidden_command
                )
                CmdExecutor.check_result(answer)
        except Exception as err:
            if check_result:
                raise CmdExecutorAnswerResultError(answer) from err

        return answer

    @staticmethod
    def run_parallely_cmds(
        cmd_list: Union[List[List[str]], List[str]]
    ) -> List[CmdExecutorParallelAnswer]:
        """Run commands parallely as subprocesses.

        Args:
            cmd_list (Union[List[List[str]], List[str]]): List with commands to run.

        Returns:
            List[CmdExecutorParallelAnswer]: List with results of commands run.
                contains attrs(pid, {exit_code, command, stdout, stderr})
        """
        results = []
        cmd_list = [CmdExecutor._prepare_command(cmd) for cmd in cmd_list]
        for cmd in cmd_list:
            logger.info(f"Run parallell process with command: {cmd.execf}")

        _proc_list = [
            subprocess.Popen(
                cmd.execf, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            for cmd in cmd_list
        ]

        # Waits until all processes will done
        for _proc in _proc_list:
            _proc.wait()
            _stdout = _proc.stdout.read().decode("utf-8")
            _stderr = _proc.stderr.read().decode("utf-8")
            proc_data = {
                "pid": _proc.pid,
                "result": CmdExecutorAnswer(
                    _proc.returncode, _proc.args, _stdout, _stderr
                ),
            }
            logger.debug(f"PID done: {_proc.pid}")
            logger.debug(f"EXITCODE: {_proc.returncode}")
            logger.debug(f"STDOUT: {_stdout}")
            logger.debug(f"STDERR: {_stderr}")
            results.append(CmdExecutorParallelAnswer(**proc_data))
        return results
