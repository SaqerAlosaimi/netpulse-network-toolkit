import importlib.util
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import MagicMock, patch

spec = importlib.util.spec_from_file_location("netpulse", Path(__file__).resolve().parents[1] / "NetPulse.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class TcpProbeTests(unittest.TestCase):
    def test_success_is_not_an_application_health_claim(self):
        with patch.object(app.socket, "create_connection", return_value=MagicMock()) as connect:
            status, message = app.tcp_probe("service.example", 443)
        self.assertEqual(status, "connected")
        self.assertIn("Application health was not tested", message)
        connect.assert_called_once_with(("service.example", 443), timeout=5)

    def test_errors_preserve_distinct_evidence(self):
        cases = [(socket.gaierror(), "dns_error"),
                 (ConnectionRefusedError(), "refused"),
                 (socket.timeout(), "timeout"),
                 (OSError(101, "unreachable"), "network_error")]
        for error, expected in cases:
            with self.subTest(expected=expected), patch.object(app.socket, "create_connection", side_effect=error):
                status, message = app.tcp_probe("service.example", 443)
                self.assertEqual(status, expected)
                self.assertNotIn("is CLOSED", message)

    def test_invalid_input_never_connects(self):
        with patch.object(app.socket, "create_connection") as connect:
            for host, port in [("", 443), ("a", 0), ("a", 65536), ("a", "443"), ("a", True)]:
                self.assertEqual(app.tcp_probe(host, port)[0], "invalid_input")
            connect.assert_not_called()

    def test_one_real_loopback_connection(self):
        # No external network traffic: verifies the actual socket context manager.
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen(1)
            self.assertEqual(app.tcp_probe("127.0.0.1", listener.getsockname()[1])[0], "connected")


class ReportTests(unittest.TestCase):
    def setUp(self):
        app.report_logs.clear()
        app.report_events.clear()

    def test_readable_and_structured_reports_preserve_results(self):
        app.add_to_report("TCP — example", "Timed out; السبب غير محسوم", "timeout")
        with tempfile.TemporaryDirectory() as directory:
            text_path, json_path = app.export_reports(Path(directory) / "sample")
            data = json.loads(Path(json_path).read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], 1)
            self.assertEqual(data["checks"][0]["status"], "timeout")
            self.assertIn("السبب", data["checks"][0]["output"])
            self.assertIn("Timed out", Path(text_path).read_text(encoding="utf-8"))
            self.assertRegex(data["checks"][0]["timestamp"], r"[+-]\d\d:\d\d$")

    def test_command_nonzero_exit_is_recorded(self):
        result = MagicMock(stdout="probe failed", stderr="", returncode=1)
        with patch.object(app.subprocess, "run", return_value=result), patch("builtins.print"):
            app.run_command(["ping", "service.example"], "Ping")
        self.assertEqual(app.report_events[0]["status"], "nonzero_exit")

    def test_missing_command_is_recorded(self):
        with patch.object(app.subprocess, "run", side_effect=FileNotFoundError()), patch("builtins.print"):
            app.run_command(["traceroute", "service.example"], "Trace")
        self.assertEqual(app.report_events[0]["status"], "unavailable")

    def test_command_timeout_is_recorded(self):
        error = app.subprocess.TimeoutExpired("ping", 1)
        with patch.object(app.subprocess, "run", side_effect=error), patch("builtins.print"):
            app.run_command(["ping", "service.example"], "Ping", timeout=1)
        self.assertEqual(app.report_events[0]["status"], "timeout")

    def test_invalid_port_from_menu_is_recorded_without_connection(self):
        with patch("builtins.input", side_effect=["service.example", "not-a-port"]), patch("builtins.print"), patch.object(app.socket, "create_connection") as connect:
            app.port_check()
            connect.assert_not_called()
        self.assertEqual(app.report_events[0]["status"], "invalid_input")


if __name__ == "__main__":
    unittest.main()
