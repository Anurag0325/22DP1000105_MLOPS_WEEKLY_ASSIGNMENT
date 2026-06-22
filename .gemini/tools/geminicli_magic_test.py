import subprocess
from unittest import mock


def mock_register_cell_magic(f):
  return f


p = mock.patch(
    "IPython.core.magic.register_cell_magic", mock_register_cell_magic
)
p.start()

from google3.cloud.ml.dset.dlenv.build.vm.packer.workbench.gemini_cli.geminicli.tools import geminicli_magic  # pylint: disable=g-import-not-at-top
from google3.testing.pybase import googletest

p.stop()


class GeminicliMagicTest(googletest.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_ipython = mock.Mock()
    self.get_ipython_patcher = mock.patch(
        "IPython.get_ipython", return_value=self.mock_ipython
    )
    self.mock_get_ipython = self.get_ipython_patcher.start()
    self.addCleanup(self.get_ipython_patcher.stop)

    self.mock_run = self.enter_context(
        mock.patch("subprocess.run", autospec=True)
    )
    self.mock_print = self.enter_context(
        mock.patch("builtins.print")
    )
    self.prompt_modifier = (
        "\n\nReturn ONLY the python code. Do not include explanations or"
        " file-writing commands."
    )

  def test_successful_run_with_markdown(self):
    self.mock_run.return_value = subprocess.CompletedProcess(
        args=["gemini", "-p", "some prompt"],
        returncode=0,
        stdout="```python\nprint('hello')\n```",
        stderr="",
    )
    geminicli_magic.geminicli_magic("", "some prompt")
    expected_prompt = "some prompt" + self.prompt_modifier
    self.mock_run.assert_called_once_with(
        ["gemini", "-p", expected_prompt],
        capture_output=True,
        text=True,
        check=True,
    )
    self.mock_ipython.set_next_input.assert_called_once_with(
        "print('hello')", replace=False
    )
    self.mock_print.assert_called_once_with(
        "✨ Code generated and placed in the cell below."
    )

  def test_successful_run_without_markdown(self):
    self.mock_run.return_value = subprocess.CompletedProcess(
        args=["gemini", "-p", "some prompt"],
        returncode=0,
        stdout="print('hello')",
        stderr="",
    )
    geminicli_magic.geminicli_magic("", "some prompt")
    expected_prompt = "some prompt" + self.prompt_modifier
    self.mock_run.assert_called_once_with(
        ["gemini", "-p", expected_prompt],
        capture_output=True,
        text=True,
        check=True,
    )
    self.mock_ipython.set_next_input.assert_called_once_with(
        "print('hello')", replace=False
    )
    self.mock_print.assert_called_once_with(
        "✨ Code generated and placed in the cell below."
    )

  def test_successful_run_with_markdown_no_lang(self):
    self.mock_run.return_value = subprocess.CompletedProcess(
        args=["gemini", "-p", "some prompt"],
        returncode=0,
        stdout="```\nprint('hello')\n```",
        stderr="",
    )
    geminicli_magic.geminicli_magic("", "some prompt")
    expected_prompt = "some prompt" + self.prompt_modifier
    self.mock_run.assert_called_once_with(
        ["gemini", "-p", expected_prompt],
        capture_output=True,
        text=True,
        check=True,
    )
    self.mock_ipython.set_next_input.assert_called_once_with(
        "print('hello')", replace=False
    )
    self.mock_print.assert_called_once_with(
        "✨ Code generated and placed in the cell below."
    )

  def test_called_process_error(self):
    self.mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd="gemini", stderr="some error"
    )
    geminicli_magic.geminicli_magic("", "some prompt")
    expected_prompt = "some prompt" + self.prompt_modifier
    self.mock_run.assert_called_once_with(
        ["gemini", "-p", expected_prompt],
        capture_output=True,
        text=True,
        check=True,
    )
    self.mock_ipython.set_next_input.assert_not_called()
    self.mock_print.assert_called_once_with("❌ CLI Error: some error")

  def test_file_not_found_error(self):
    self.mock_run.side_effect = FileNotFoundError()
    geminicli_magic.geminicli_magic("", "some prompt")
    expected_prompt = "some prompt" + self.prompt_modifier
    self.mock_run.assert_called_once_with(
        ["gemini", "-p", expected_prompt],
        capture_output=True,
        text=True,
        check=True,
    )
    self.mock_ipython.set_next_input.assert_not_called()
    self.mock_print.assert_called_once_with(
        "❌ CLI Error: 'gemini' command not found. Is it installed and in your"
        " PATH?"
    )

  def test_os_error(self):
    self.mock_run.side_effect = OSError("some OS error")
    geminicli_magic.geminicli_magic("", "some prompt")
    expected_prompt = "some prompt" + self.prompt_modifier
    self.mock_run.assert_called_once_with(
        ["gemini", "-p", expected_prompt],
        capture_output=True,
        text=True,
        check=True,
    )
    self.mock_ipython.set_next_input.assert_not_called()
    self.mock_print.assert_called_once_with(
        "❌ OS Error: Failed to run gemini CLI: some OS error"
    )

  def test_ipython_error(self):
    self.get_ipython_patcher.stop()
    self.get_ipython_patcher = mock.patch(
        "IPython.get_ipython", return_value=None
    )
    self.get_ipython_patcher.start()
    self.mock_run.return_value = subprocess.CompletedProcess(
        args=["gemini", "-p", "some prompt"],
        returncode=0,
        stdout="print('hello')",
        stderr="",
    )
    geminicli_magic.geminicli_magic("", "some prompt")
    expected_prompt = "some prompt" + self.prompt_modifier
    self.mock_run.assert_called_once_with(
        ["gemini", "-p", expected_prompt],
        capture_output=True,
        text=True,
        check=True,
    )
    self.mock_print.assert_called_once_with(
        "❌ IPython Error: Could not get IPython instance to set next input."
    )

if __name__ == "__main__":
  googletest.main()
