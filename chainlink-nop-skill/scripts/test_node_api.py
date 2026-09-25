#!/usr/bin/env python3
"""Deterministic tests for the bundled node API client."""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import node_api  # noqa: E402


class ApiHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        state = self.server.state
        state["requests"].append(
            {
                "method": self.command,
                "path": self.path,
                "key": self.headers.get("X-API-KEY"),
                "secret": self.headers.get("X-API-SECRET"),
            }
        )
        result = state["router"](self.path)
        status, body, content_type = result[:3]
        response_headers = result[3] if len(result) == 4 else {}
        if isinstance(body, (dict, list)) or body is None:
            raw = b"" if body is None else json.dumps(body).encode()
        elif isinstance(body, bytes):
            raw = body
        else:
            raw = str(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        for name, value in response_headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args: object) -> None:
        pass


class NodeApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.server = HTTPServer(("127.0.0.1", 0), ApiHandler)
        self.server.state = {
            "requests": [],
            "router": lambda path: (
                200,
                {"data": [], "meta": {"count": 0}},
                "application/json",
            ),
        }
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        host, port = self.server.server_address
        self.origin = f"http://{host}:{port}"

    @property
    def requests(self) -> list[dict[str, str]]:
        return self.server.state["requests"]

    def set_router(self, router: object) -> None:
        self.server.state["router"] = router

    def env_file(self, **values: str) -> Path:
        path = self.directory / "test.env"
        path.write_text("".join(f"{key}={value}\n" for key, value in values.items()))
        return path

    def config_file(
        self,
        *,
        key_kind: str = "env",
        key_value: str = "NODE_KEY",
        secret_kind: str = "env",
        secret_value: str = "NODE_SECRET",
        origin: str | None = None,
    ) -> Path:
        path = self.directory / "config.yaml"
        path.write_text(
            "schema_version: 1\n"
            "node_api:\n"
            f"  url: {origin or self.origin}\n"
            "  api_key:\n"
            f"    {key_kind}: {key_value}\n"
            "  api_secret:\n"
            f"    {secret_kind}: {secret_value}\n"
        )
        return path

    def client(self) -> node_api.NodeApiClient:
        return node_api.NodeApiClient(
            self.origin,
            ("env", "NODE_KEY"),
            ("env", "NODE_SECRET"),
            {"NODE_KEY": "test-key", "NODE_SECRET": "test-secret"},
            timeout=2,
        )

    def test_env_file_overlays_environment_and_does_not_evaluate_shell(self) -> None:
        env_path = self.env_file(
            CHAINLINK_API_URL=self.origin,
            CHAINLINK_API_KEY="overlay-key",
            CHAINLINK_API_SECRET="$(not-a-command)",
        )
        with mock.patch.dict(
            os.environ,
            {
                "CHAINLINK_API_URL": "https://wrong.example",
                "CHAINLINK_API_KEY": "wrong-key",
                "CHAINLINK_API_SECRET": "wrong-secret",
            },
        ):
            connection = node_api.load_connection(
                self.directory / "absent.yaml", env_path
            )
            node_api.NodeApiClient(*connection, timeout=2).get("/v2/ping")

        self.assertEqual(self.requests[0]["key"], "overlay-key")
        self.assertEqual(self.requests[0]["secret"], "$(not-a-command)")

    def test_fixed_config_schema_and_request_time_env_file_references(self) -> None:
        secret_path = self.directory / "secret"
        secret_path.write_text("first-secret\n")
        config = self.config_file(
            secret_kind="file", secret_value=str(secret_path)
        )
        origin, key_reference, secret_reference = node_api.parse_config(config)
        client = node_api.NodeApiClient(
            origin, key_reference, secret_reference, timeout=2
        )

        with mock.patch.dict(os.environ, {"NODE_KEY": "first-key"}):
            client.get("/one")
            os.environ["NODE_KEY"] = "second-key"
            secret_path.write_text("second-secret\n")
            client.get("/two")

        self.assertEqual(
            [(item["key"], item["secret"]) for item in self.requests],
            [("first-key", "first-secret"), ("second-key", "second-secret")],
        )
        bad = self.directory / "bad.yaml"
        bad.write_text(config.read_text() + "unsupported: true\n")
        with self.assertRaises(node_api.ConfigError):
            node_api.parse_config(bad)

    def test_config_rejects_non_http_and_non_origin_urls(self) -> None:
        for value in (
            "file:///tmp/node",
            "ftp://node.example",
            "https://node.example/path",
            "https://user:pass@node.example",
        ):
            with self.subTest(value=value):
                config = self.config_file(origin=value)
                with self.assertRaises(node_api.ConfigError):
                    node_api.parse_config(config)

    def test_headers_and_method_are_get_only(self) -> None:
        self.client().get("/v2/jobs")
        self.assertEqual(
            self.requests,
            [
                {
                    "method": "GET",
                    "path": "/v2/jobs",
                    "key": "test-key",
                    "secret": "test-secret",
                }
            ],
        )

    def test_snapshot_is_broad_compact_and_continues_after_http_errors(self) -> None:
        def router(path: str) -> tuple[int, object, str]:
            if path == "/health":
                return 200, "healthy", "text/plain"
            if path == "/v2/jobs":
                return 503, {"api_secret": "must-not-appear"}, "application/json"
            return 200, {"data": [{"id": path}], "meta": {"count": 1}}, "application/json"

        self.set_router(router)
        result = self.client().snapshot()

        self.assertEqual(set(result), set(node_api.SNAPSHOT_PATHS))
        self.assertEqual([item["path"] for item in self.requests], list(node_api.SNAPSHOT_PATHS))
        self.assertEqual(
            result["/health"],
            {"status": 200, "count": None, "type": "string", "error": None},
        )
        self.assertEqual(
            result["/v2/jobs"],
            {"status": 503, "count": 1, "type": "object", "error": "HTTP 503"},
        )
        self.assertEqual(set(result["/v2/keys/dkgrecipient"]), {"status", "count", "type", "error"})
        self.assertNotIn("must-not-appear", json.dumps(result))

    def test_all_pages_combines_data_preserves_meta_and_stops_repeat(self) -> None:
        second = f"{self.origin}/v2/jobs?cursor=second"

        def router(path: str) -> tuple[int, object, str]:
            if path == "/v2/jobs":
                return (
                    200,
                    {
                        "data": [{"id": "one", "outgoingToken": "hide-one"}],
                        "meta": {"count": 2, "diagnostic": "kept"},
                        "links": {"next": second},
                    },
                    "application/vnd.api+json",
                )
            return (
                200,
                {
                    "data": [{"id": "two", "api_secret": "hide-two"}],
                    "meta": {"count": 2},
                    "links": {"next": second},
                },
                "application/vnd.api+json",
            )

        self.set_router(router)
        body = self.client().get("/v2/jobs", all_pages=True)

        self.assertEqual([item["id"] for item in body["data"]], ["one", "two"])
        self.assertEqual(body["meta"], {"count": 2, "diagnostic": "kept"})
        self.assertEqual(body["links"], {"next": second})
        self.assertEqual(body["data"][0]["outgoingToken"], node_api.REDACTED)
        self.assertEqual(body["data"][1]["api_secret"], node_api.REDACTED)
        self.assertEqual(len(self.requests), 2)

    def test_all_pages_rejects_cross_origin_next_without_requesting_it(self) -> None:
        self.set_router(
            lambda path: (
                200,
                {
                    "data": [],
                    "meta": {"count": 0},
                    "links": {"next": "https://other.example/v2/jobs?page=2"},
                },
                "application/json",
            )
        )
        with self.assertRaisesRegex(node_api.RequestError, "same-origin"):
            self.client().get("/v2/jobs", all_pages=True)
        self.assertEqual(len(self.requests), 1)

    def test_cross_origin_redirect_is_rejected_before_credentials_are_forwarded(self) -> None:
        self.set_router(
            lambda path: (
                302,
                None,
                "text/plain",
                {"Location": "http://127.0.0.1:1/capture"},
            )
        )
        with self.assertRaisesRegex(node_api.RequestError, "same-origin"):
            self.client().get("/redirect")
        self.assertEqual(len(self.requests), 1)

    def test_recursive_response_redaction_retains_diagnostics_and_public_keys(self) -> None:
        self.set_router(
            lambda path: (
                200,
                {
                    "data": [
                        {
                            "id": "bridge-1",
                            "outgoingToken": "secret-a",
                            "nested": {"API_KEY": "secret-b", "healthy": True},
                            "publicKey": "0xdiagnostic",
                        }
                    ],
                    "meta": {"count": 1},
                },
                "application/json",
            )
        )
        body = self.client().get("/v2/bridge_types")
        item = body["data"][0]
        self.assertEqual(item["outgoingToken"], node_api.REDACTED)
        self.assertEqual(item["nested"]["API_KEY"], node_api.REDACTED)
        self.assertTrue(item["nested"]["healthy"])
        self.assertEqual(item["publicKey"], "0xdiagnostic")

    def test_secret_like_toml_assignments_are_redacted(self) -> None:
        source = (
            '[Database]\nPassword = "db-secret"\n'
            'Log.Level = "debug"\nAPIKey="api-secret"\nPublicKey = "keep"\n'
        )
        redacted = node_api.redact_toml(source)
        self.assertIn('Password = "[REDACTED]"', redacted)
        self.assertIn('APIKey="[REDACTED]"', redacted)
        self.assertIn('Log.Level = "debug"', redacted)
        self.assertIn('PublicKey = "keep"', redacted)
        self.assertNotIn("db-secret", redacted)
        self.assertNotIn("api-secret", redacted)

    def test_http_error_exits_nonzero_without_printing_credentials_or_body(self) -> None:
        self.set_router(
            lambda path: (
                500,
                {"api_secret": "response-canary"},
                "application/json",
            )
        )
        env_path = self.env_file(
            CHAINLINK_API_URL=self.origin,
            CHAINLINK_API_KEY="request-key-canary",
            CHAINLINK_API_SECRET="request-secret-canary",
        )
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = node_api.main(
                [
                    "--config",
                    str(self.directory / "absent.yaml"),
                    "--env-file",
                    str(env_path),
                    "get",
                    "/failure",
                ]
            )

        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")
        error = json.loads(stderr.getvalue())
        self.assertEqual(error, {"error": "HTTP 500"})
        for canary in (
            "request-key-canary",
            "request-secret-canary",
            "response-canary",
        ):
            self.assertNotIn(canary, stderr.getvalue())

    def test_get_rejects_non_root_absolute_and_fragment_paths_before_request(self) -> None:
        client = self.client()
        for path in (
            "v2/jobs",
            "https://other.example/v2/jobs",
            "//other.example/v2/jobs",
            "/v2/jobs#fragment",
            "/v2/\\jobs",
        ):
            with self.subTest(path=path), self.assertRaises(node_api.RequestError):
                client.get(path)
        self.assertEqual(self.requests, [])

    def test_summary_count_and_type_rules(self) -> None:
        cases = (
            ({"value": 1}, 1, "object"),
            ({"data": {}}, 1, "object"),
            ({"data": None}, 0, "object"),
            ({"data": []}, 0, "object"),
            ([], 0, "array"),
            ("text", None, "string"),
            (None, None, "null"),
        )
        for body, count, kind in cases:
            with self.subTest(body=body):
                summary = node_api.summarize(node_api.Response(200, body, self.origin))
                self.assertEqual(summary["count"], count)
                self.assertEqual(summary["type"], kind)

    def test_script_runs_via_python_and_emits_only_json_stdout(self) -> None:
        self.set_router(
            lambda path: (
                200,
                {"data": {"id": "build"}, "meta": {"count": 1}},
                "application/json",
            )
        )
        env_path = self.env_file(
            CHAINLINK_API_URL=self.origin,
            CHAINLINK_API_KEY="key",
            CHAINLINK_API_SECRET="secret",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(Path(node_api.__file__).resolve()),
                "--config",
                str(self.directory / "absent.yaml"),
                "--env-file",
                str(env_path),
                "get",
                "/v2/build_info",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["data"]["id"], "build")
        self.assertEqual(completed.stderr, "")


if __name__ == "__main__":
    unittest.main()
