#!/usr/bin/env python3
"""Small, GET-only Chainlink node API diagnostic client."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping


DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"
REDACTED = "[REDACTED]"
ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
YAML_LINE = re.compile(r"^( *)([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$")
TOML_ASSIGNMENT = re.compile(r"^(\s*)([A-Za-z0-9_.-]+)(\s*=\s*)(.*)$")

SNAPSHOT_PATHS = (
    "/health",
    "/readyz",
    "/v2/ping",
    "/v2/build_info",
    "/v2/config",
    "/v2/config/v2",
    "/v2/features",
    "/v2/log",
    "/v2/bridge_types",
    "/v2/external_initiators",
    "/v2/jobs",
    "/v2/pipeline/runs",
    "/v2/chains",
    "/v2/nodes",
    "/v2/transactions",
    "/v2/transactions/evm",
    "/v2/tx_attempts",
    "/v2/tx_attempts/evm",
    "/v2/keys/csa",
    "/v2/keys/eth",
    "/v2/keys/evm",
    "/v2/keys/ocr",
    "/v2/keys/ocr2",
    "/v2/keys/p2p",
    "/v2/keys/solana",
    "/v2/keys/cosmos",
    "/v2/keys/starknet",
    "/v2/keys/aptos",
    "/v2/keys/stellar",
    "/v2/keys/tron",
    "/v2/keys/sui",
    "/v2/keys/ton",
    "/v2/keys/vrf",
    "/v2/keys/workflow",
    "/v2/keys/dkgrecipient",
)


class CliError(Exception):
    """A safe-to-display command error."""


class ConfigError(CliError):
    """Invalid configuration or unresolved credential reference."""


class RequestError(CliError):
    """A request could not be made or safely followed."""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliError("invalid command arguments")


class Response:
    def __init__(self, status: int, body: Any, url: str) -> None:
        self.status = status
        self.body = body
        self.url = url


def _without_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if character in ("'", '"'):
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
            continue
        if character == "#" and quote is None and (
            index == 0 or value[index - 1].isspace()
        ):
            return value[:index].rstrip()
    if quote is not None:
        raise ConfigError("unterminated quoted value")
    return value.rstrip()


def _parse_scalar(value: str, context: str) -> str:
    value = _without_comment(value).strip()
    if not value:
        raise ConfigError(f"missing {context}")
    if value[0] == "'":
        if len(value) < 2 or value[-1] != "'":
            raise ConfigError(f"invalid quoted {context}")
        return value[1:-1].replace("''", "'")
    if value[0] == '"':
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError) as error:
            raise ConfigError(f"invalid quoted {context}") from error
        if not isinstance(parsed, str):
            raise ConfigError(f"invalid {context}")
        return parsed
    if value[-1:] in ("'", '"'):
        raise ConfigError(f"invalid quoted {context}")
    return value


def parse_env_file(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise ConfigError("cannot read environment file") from error

    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ConfigError(f"invalid environment file line {line_number}")
        name, raw_value = line.split("=", 1)
        name = name.strip()
        if not ENV_NAME.fullmatch(name):
            raise ConfigError(f"invalid environment name on line {line_number}")
        cleaned = _without_comment(raw_value).strip()
        values[name] = (
            _parse_scalar(raw_value, f"environment value on line {line_number}")
            if cleaned
            else ""
        )
    return values


def _validate_origin(value: str) -> str:
    if any(character.isspace() or ord(character) < 32 for character in value):
        raise ConfigError("node API URL must be an HTTP(S) origin")
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError as error:
        raise ConfigError("node API URL must be an HTTP(S) origin") from error
    if (
        parsed.scheme.lower() not in ("http", "https")
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ConfigError("node API URL must be an HTTP(S) origin")
    if port is not None and not 0 < port < 65536:
        raise ConfigError("node API URL must be an HTTP(S) origin")
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc, "", "", "")
    )


def _validate_reference(kind: str, value: str) -> tuple[str, str]:
    if kind == "env":
        if not ENV_NAME.fullmatch(value):
            raise ConfigError("credential environment reference is invalid")
    elif kind == "file":
        if not Path(value).is_absolute():
            raise ConfigError("credential file reference must be absolute")
    else:
        raise ConfigError("credential reference must use env or file")
    return kind, value


def parse_config(path: Path) -> tuple[str, tuple[str, str], tuple[str, str]]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise ConfigError("cannot read config file") from error

    values: dict[tuple[str, ...], str] = {}
    mappings: set[tuple[str, ...]] = set()
    parent: tuple[str, ...] = ()

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise ConfigError(f"invalid config indentation on line {line_number}")
        match = YAML_LINE.fullmatch(raw_line.rstrip())
        if not match:
            raise ConfigError(f"invalid config syntax on line {line_number}")
        spaces, key, raw_value = match.groups()
        indent = len(spaces)
        raw_value = raw_value or ""

        if indent == 0:
            item = (key,)
            parent = item if not _without_comment(raw_value).strip() else ()
        elif indent == 2 and ("node_api",) in mappings:
            item = ("node_api", key)
            parent = item if not _without_comment(raw_value).strip() else ("node_api",)
        elif indent == 4 and parent in (
            ("node_api", "api_key"),
            ("node_api", "api_secret"),
        ):
            item = (*parent, key)
        else:
            raise ConfigError(f"invalid config structure on line {line_number}")

        if item in values or item in mappings:
            raise ConfigError(f"duplicate config field on line {line_number}")
        if not _without_comment(raw_value).strip():
            mappings.add(item)
        else:
            values[item] = _parse_scalar(raw_value, "config value")

    expected_mappings = {
        ("node_api",),
        ("node_api", "api_key"),
        ("node_api", "api_secret"),
    }
    if mappings != expected_mappings:
        raise ConfigError("config must use the documented schema")
    if set(values) - {
        ("schema_version",),
        ("node_api", "url"),
        ("node_api", "api_key", "env"),
        ("node_api", "api_key", "file"),
        ("node_api", "api_secret", "env"),
        ("node_api", "api_secret", "file"),
    }:
        raise ConfigError("config contains an unsupported field")
    if values.get(("schema_version",)) != "1":
        raise ConfigError("config schema_version must be 1")
    if ("node_api", "url") not in values:
        raise ConfigError("config is missing node_api.url")

    references: list[tuple[str, str]] = []
    for credential in ("api_key", "api_secret"):
        entries = [
            (field[-1], value)
            for field, value in values.items()
            if field[:2] == ("node_api", credential) and len(field) == 3
        ]
        if len(entries) != 1:
            raise ConfigError(f"config {credential} must contain exactly one reference")
        references.append(_validate_reference(*entries[0]))

    return _validate_origin(values[("node_api", "url")]), references[0], references[1]


def load_connection(
    config_path: Path, env_file: Path | None
) -> tuple[str, tuple[str, str], tuple[str, str], Mapping[str, str]]:
    overlay = parse_env_file(env_file) if env_file else {}
    if config_path.exists():
        origin, key_reference, secret_reference = parse_config(config_path)
    else:

        def environment(name: str) -> str | None:
            return overlay.get(name, os.environ.get(name))

        raw_origin = environment("CHAINLINK_API_URL")
        if raw_origin is None:
            raise ConfigError("config is absent and CHAINLINK_API_URL is not set")
        origin = _validate_origin(raw_origin)
        key_reference = ("direct_env", "CHAINLINK_API_KEY")
        secret_reference = ("direct_env", "CHAINLINK_API_SECRET")
    return origin, key_reference, secret_reference, overlay


def _origin_tuple(url: str) -> tuple[str, str, int]:
    parsed = urllib.parse.urlsplit(url)
    default_port = 443 if parsed.scheme.lower() == "https" else 80
    return parsed.scheme.lower(), (parsed.hostname or "").lower(), parsed.port or default_port


class SameOriginRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, origin: tuple[str, str, int]) -> None:
        super().__init__()
        self.origin = origin

    def redirect_request(
        self,
        request: urllib.request.Request,
        file_pointer: Any,
        code: int,
        message: str,
        headers: Mapping[str, str],
        new_url: str,
    ) -> urllib.request.Request | None:
        target = urllib.parse.urljoin(request.full_url, new_url)
        try:
            parsed = urllib.parse.urlsplit(target)
            target_origin = _origin_tuple(target)
        except ValueError as error:
            raise RequestError("redirect target is invalid") from error
        if (
            parsed.scheme.lower() not in ("http", "https")
            or parsed.username is not None
            or parsed.password is not None
            or target_origin != self.origin
        ):
            raise RequestError("redirect target must be same-origin")
        return super().redirect_request(
            request, file_pointer, code, message, headers, target
        )


def _sensitive_key(key: Any) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", str(key).lower())
    if "publickey" in normalized:
        return False
    return any(
        marker in normalized
        for marker in (
            "password",
            "passwd",
            "secret",
            "credential",
            "token",
            "apikey",
            "accesskey",
            "privatekey",
            "authorization",
            "cookie",
            "connectionstring",
        )
    )


def redact_toml(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines(keepends=True):
        ending = ""
        content = line
        if content.endswith("\r\n"):
            content, ending = content[:-2], "\r\n"
        elif content.endswith(("\n", "\r")):
            content, ending = content[:-1], content[-1]
        match = TOML_ASSIGNMENT.fullmatch(content)
        if match and _sensitive_key(match.group(2).split(".")[-1]):
            content = "".join(match.groups()[:3]) + '"' + REDACTED + '"'
        lines.append(content + ending)
    return "".join(lines)


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: REDACTED if _sensitive_key(key) else sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        return redact_toml(value)
    return value


class NodeApiClient:
    def __init__(
        self,
        origin: str,
        key_reference: tuple[str, str],
        secret_reference: tuple[str, str],
        env_overlay: Mapping[str, str] | None = None,
        timeout: float = 15,
    ) -> None:
        self.origin = _validate_origin(origin)
        self.key_reference = key_reference
        self.secret_reference = secret_reference
        self.env_overlay = env_overlay or {}
        self.timeout = timeout
        self._origin = _origin_tuple(self.origin)
        self._opener = urllib.request.build_opener(
            SameOriginRedirectHandler(self._origin)
        )

    def _resolve(self, reference: tuple[str, str], label: str) -> str:
        kind, location = reference
        if kind in ("env", "direct_env"):
            value = self.env_overlay.get(location, os.environ.get(location))
            if value is None or not value.strip():
                raise ConfigError(f"cannot resolve {label} environment reference")
            return value
        if kind == "file":
            try:
                value = Path(location).read_text(encoding="utf-8").strip()
            except (OSError, UnicodeError) as error:
                raise ConfigError(f"cannot resolve {label} file reference") from error
            if not value:
                raise ConfigError(f"cannot resolve {label} file reference")
            return value
        raise ConfigError(f"cannot resolve {label} reference")

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json, application/vnd.api+json, text/plain",
            "X-API-KEY": self._resolve(self.key_reference, "API key"),
            "X-API-SECRET": self._resolve(self.secret_reference, "API secret"),
        }

    def _url(self, reference: str, *, initial: bool) -> str:
        if not isinstance(reference, str) or not reference:
            raise RequestError("GET path is missing")
        if any(ord(character) < 32 for character in reference) or "\\" in reference:
            raise RequestError("GET path is invalid")
        parsed_reference = urllib.parse.urlsplit(reference)
        if initial:
            if (
                not reference.startswith("/")
                or reference.startswith("//")
                or parsed_reference.scheme
                or parsed_reference.netloc
                or parsed_reference.fragment
            ):
                raise RequestError("GET path must be root-relative")
            return self.origin + reference

        absolute = urllib.parse.urljoin(self.origin + "/", reference)
        try:
            parsed = urllib.parse.urlsplit(absolute)
            origin = _origin_tuple(absolute)
        except ValueError as error:
            raise RequestError("pagination next link is invalid") from error
        if (
            parsed.scheme.lower() not in ("http", "https")
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
            or origin != self._origin
        ):
            raise RequestError("pagination next link must be same-origin")
        return absolute

    def request(self, reference: str, *, initial: bool = True) -> Response:
        url = self._url(reference, initial=initial)
        request = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            opened = self._opener.open(request, timeout=self.timeout)
        except urllib.error.HTTPError as error:
            opened = error
        except RequestError:
            raise
        except (
            urllib.error.URLError,
            OSError,
            ValueError,
            http.client.HTTPException,
        ) as error:
            reason = getattr(error, "reason", None)
            detail = str(reason) if reason is not None else error.__class__.__name__
            raise RequestError(f"request failed: {detail}") from error

        try:
            with opened as response:
                raw = response.read()
                status = response.getcode()
                charset = response.headers.get_content_charset() or "utf-8"
                final_url = response.geturl()
        except (OSError, ValueError, http.client.HTTPException) as error:
            raise RequestError(f"request failed: {error.__class__.__name__}") from error
        try:
            text = raw.decode(charset, errors="replace")
        except LookupError:
            text = raw.decode("utf-8", errors="replace")
        if not text.strip():
            body: Any = None
        else:
            try:
                body = json.loads(text)
            except json.JSONDecodeError:
                body = text
        return Response(status, body, final_url)

    def get(self, path: str, all_pages: bool = False) -> Any:
        response = self.request(path)
        if response.status >= 400:
            raise RequestError(f"HTTP {response.status}")
        if not all_pages:
            return sanitize(response.body)
        if not isinstance(response.body, dict) or not isinstance(
            response.body.get("data"), list
        ):
            raise RequestError("--all-pages requires a JSON:API collection")

        combined = dict(response.body)
        combined["data"] = list(response.body["data"])
        seen_urls = {response.url}
        seen_cursors: set[tuple[str, ...]] = set()
        current = response.body

        while True:
            links = current.get("links")
            next_link = links.get("next") if isinstance(links, dict) else None
            if next_link in (None, ""):
                break
            if not isinstance(next_link, str):
                raise RequestError("pagination next link is invalid")
            next_url = self._url(next_link, initial=False)
            cursor = tuple(
                urllib.parse.parse_qs(
                    urllib.parse.urlsplit(next_url).query, keep_blank_values=True
                ).get("cursor", ())
            )
            if next_url in seen_urls or (cursor and cursor in seen_cursors):
                break
            seen_urls.add(next_url)
            if cursor:
                seen_cursors.add(cursor)

            response = self.request(next_url, initial=False)
            if response.status >= 400:
                raise RequestError(f"HTTP {response.status} during pagination")
            if not isinstance(response.body, dict) or not isinstance(
                response.body.get("data"), list
            ):
                raise RequestError("paginated response is not a JSON:API collection")
            combined["data"].extend(response.body["data"])
            current = response.body
        return sanitize(combined)

    def snapshot(self) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for path in SNAPSHOT_PATHS:
            try:
                response = self.request(path)
                result[path] = summarize(response)
            except ConfigError:
                raise
            except RequestError as error:
                result[path] = {
                    "status": None,
                    "count": None,
                    "type": None,
                    "error": str(error),
                }
        return result


def _json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    return "unknown"


def _resource_count(body: Any) -> int | None:
    if isinstance(body, dict):
        meta = body.get("meta")
        if isinstance(meta, dict) and isinstance(meta.get("count"), int):
            return meta["count"]
        if "data" in body:
            data = body["data"]
            if isinstance(data, list):
                return len(data)
            return 0 if data is None else 1
        return 1
    if isinstance(body, list):
        return len(body)
    return None


def summarize(response: Response) -> dict[str, Any]:
    return {
        "status": response.status,
        "count": _resource_count(response.body),
        "type": _json_type(response.body),
        "error": None if response.status < 400 else f"HTTP {response.status}",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--env-file", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("snapshot", help="query a broad diagnostic route set")
    get_parser = commands.add_parser("get", help="send one root-relative GET")
    get_parser.add_argument("path")
    get_parser.add_argument("--all-pages", action="store_true")
    return parser


def run(arguments: list[str] | None = None) -> Any:
    options = build_parser().parse_args(arguments)
    connection = load_connection(options.config, options.env_file)
    client = NodeApiClient(*connection)
    if options.command == "snapshot":
        return client.snapshot()
    return client.get(options.path, options.all_pages)


def main(arguments: list[str] | None = None) -> int:
    try:
        output = run(arguments)
    except CliError as error:
        print(
            json.dumps({"error": str(error)}, separators=(",", ":")),
            file=sys.stderr,
        )
        return 1
    except Exception:
        print(
            json.dumps(
                {"error": "unexpected node API client error"}, separators=(",", ":")
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(output, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
