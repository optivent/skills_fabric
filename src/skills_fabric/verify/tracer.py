"""Execution Tracer for behavioral understanding."""
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TraceEntry:
    event: str
    function: str
    filename: str
    line: int
    return_value: Optional[str] = None

@dataclass
class ExecutionTrace:
    entries: list = field(default_factory=list)
    stdout: str = ''
    stderr: str = ''
    success: bool = False
    
    def get_call_sequence(self) -> list[str]:
        return [e.function for e in self.entries if e.event == 'call']

class ExecutionTracer:
    def trace(self, code: str, timeout: int = 10) -> ExecutionTrace:
        traced = self._wrap_with_tracer(code)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(traced)
            script = f.name
        trace = ExecutionTrace()
        try:
            result = subprocess.run(
                ['bwrap', '--ro-bind', '/', '/', '--dev', '/dev', '--proc', '/proc',
                 '--unshare-net', '--', 'python3', script],
                capture_output=True, text=True, timeout=timeout)
            trace.stdout = result.stdout
            trace.stderr = result.stderr
            trace.success = result.returncode == 0
            trace.entries = self._parse_trace(result.stderr)
        except subprocess.TimeoutExpired:
            trace.stderr = 'Timeout'
        finally:
            Path(script).unlink()
        return trace
    
    def _wrap_with_tracer(self, code: str) -> str:
        indent = '\n'.join('    ' + l for l in code.split('\n'))
        return f'''
import sys, json
_out = []
def _t(f, e, a):
    if e in ('call','return'):
        _out.append({{'event':e,'function':f.f_code.co_name,'filename':f.f_code.co_filename,'line':f.f_lineno}})
    return _t
sys.settrace(_t)
try:
{indent}
finally:
    sys.settrace(None)
    for x in _out: print(json.dumps(x), file=sys.stderr)
'''
    
    def _parse_trace(self, stderr: str) -> list[TraceEntry]:
        entries = []
        for line in stderr.split('\n'):
            if line.startswith('{'):
                try:
                    d = json.loads(line)
                    entries.append(TraceEntry(**d))
                except: pass
        return entries
