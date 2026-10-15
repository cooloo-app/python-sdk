import json
import os
import subprocess
import sys
import unittest
from cooloo.client import EventStream, CoolooError, SendOutcomeUnknown


def run_script(script, *, timeout=2, sending=False):
    return EventStream([sys.executable, "-u", "-c", script], dict(os.environ), None, timeout, None, sending)


class ProcessTests(unittest.TestCase):
    def test_stderr_drain_and_terminal(self):
        with run_script('import sys; sys.stderr.write("x"*1000000); print(\'{"schema":1,"type":"result"}\')') as events:
            self.assertEqual(list(events)[0]["type"], "result")
            self.assertLessEqual(len(events._diagnostics), 16)

    def test_truncated_and_nonzero(self):
        scripts = ['print("not-json")',
                   'print(\'{"schema":2,"type":"result"}\')',
                   'print(\'{"schema":1,"type":"message"}\')',
                   'print(\'{"schema":1,"type":"result"}\'); raise SystemExit(1)',
                   'print(\'{"schema":1,"type":"result"}\'); print(\'{"schema":1,"type":"end"}\')',
                   'print("x"*150000)']
        for script in scripts:
            with self.subTest(script=script):
                with run_script(script) as events:
                    with self.assertRaises(CoolooError):
                        list(events)
                    self.assertIsNotNone(events._proc.poll())

    def test_send_unknown_timeout_and_eof(self):
        for script in ('import time; time.sleep(10)', 'pass'):
            with run_script(script, timeout=.15, sending=True) as events:
                with self.assertRaises(SendOutcomeUnknown):
                    list(events)
                self.assertIsNotNone(events._proc.poll())

    def test_error_and_cancel_backpressure(self):
        with run_script('print(\'{"schema":1,"type":"error","code":"forbidden","message":"no"}\')') as events:
            with self.assertRaises(CoolooError) as error:
                list(events)
            self.assertEqual(error.exception.code, "forbidden")
        with run_script('while True: print(\'{"schema":1,"type":"message"}\')') as events:
            next(events)
        self.assertIsNotNone(events._proc.poll())
        self.assertFalse(any(t.is_alive() for t in events._threads))


if __name__ == "__main__":
    unittest.main()
