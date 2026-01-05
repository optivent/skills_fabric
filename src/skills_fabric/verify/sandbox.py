"""Bubblewrap sandbox for safe code execution."""
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionResult:
    """Result of sandbox execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int


class BubblewrapSandbox:
    """Execute code safely in a Bubblewrap sandbox."""
    
    def __init__(self):
        self._check_bwrap()
    
    def _check_bwrap(self) -> bool:
        """Check if Bubblewrap is available."""
        try:
            result = subprocess.run(["which", "bwrap"], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def execute_python(self, code: str, timeout: int = 10) -> ExecutionResult:
        """Execute Python code in a sandbox."""
        try:
            # Write code to temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                code_file = f.name
            
            # Execute in sandbox
            cmd = [
                "bwrap",
                "--ro-bind", "/", "/",
                "--dev", "/dev",
                "--proc", "/proc",
                "--unshare-net",  # No network
                "--",
                "python3", code_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Cleanup
            Path(code_file).unlink()
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="Execution timed out",
                exit_code=-1
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1
            )
    
    def verify_skill(self, skill_code: str) -> bool:
        """Verify a skill's code can execute."""
        result = self.execute_python(skill_code, timeout=5)
        return result.success
