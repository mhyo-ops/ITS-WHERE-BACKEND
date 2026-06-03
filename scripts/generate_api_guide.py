import httpx
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8001"
OUTPUT_FILE = Path(__file__).parent.parent / "FRONTEND_API_GUIDE.md"


def fetch_openapi() -> dict:
    r = httpx.get(f"{BASE_URL}/openapi.json")
    r.raise_for_status()
    return r.json()


def get_method_color(method: str) -> str:
    return {"get": "🟢", "post": "🔵", "put": "🟡", "delete": "🔴"}.get(method, "⚪")


def is_protected(operation: dict) -> bool:
    security = operation.get("security", [])
    return len(security) > 0


def get_tag(operation: dict) -> str:
    tags = operation.get("tags", ["General"])
    return tags[0] if tags else "General"


def resolve_schema(schema: dict, components: dict) -> dict:
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        return components.get("schemas", {}).get(ref, {})
    return schema


def schema_to_example(schema: dict, components: dict, _depth: int = 0) -> any:
    if _depth > 3:
        return "..."
    schema = resolve_schema(schema, components)
    t = schema.get("type")
    if "allOf" in schema:
        return schema_to_example(schema["allOf"][0], components, _depth)
    if "properties" in schema:
        return {
            k: schema_to_example(v, components, _depth + 1)
            for k, v in schema.get("properties", {}).items()
            if k not in ("updated_at", "created_at", "hashed_password")
        }
    if t == "array":
        items = schema.get("items", {})
        return [schema_to_example(items, components, _depth + 1)]
    examples = {
        "string": "string",
        "integer": 1,
        "number": 1.0,
        "boolean": True,
    }
    if "enum" in schema:
        return schema["enum"][0]
    if "default" in schema:
        return schema["default"]
    return examples.get(t, "value")


def get_request_body_example(operation: dict, components: dict) -> str | None:
    rb = operation.get("requestBody")
    if not rb:
        return None
    content = rb.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})
    if not schema:
        return None
    example = schema_to_example(schema, components)
    return json.dumps(example, indent=2, ensure_ascii=False)


def get_response_example(operation: dict, components: dict) -> str | None:
    responses = operation.get("responses", {})
    for code in ("200", "201"):
        resp = responses.get(code)
        if not resp:
            continue
        content = resp.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})
        if not schema:
            continue
        example = schema_to_example(schema, components)
        return json.dumps(example, indent=2, ensure_ascii=False)
    return None


def get_query_params(operation: dict) -> list[dict]:
    return [
        p for p in operation.get("parameters", [])
        if p.get("in") == "query"
    ]


def build_curl(
    method: str,
    path: str,
    operation: dict,
    components: dict
) -> str:
    url = f"{BASE_URL}{path}"
    params = get_query_params(operation)
    if params:
        example_params = "&".join(
            f"{p['name']}={schema_to_example(p.get('schema', {}), components)}"
            for p in params[:3]
        )
        url += f"?{example_params}"

    lines = [f"curl -sS -X {method.upper()} '{url}'"]

    if is_protected(operation):
        lines.append("  -H 'Authorization: Bearer <your_token>'")

    lines.append("  -H 'Content-Type: application/json'")

    body = get_request_body_example(operation, components)
    if body:
        lines.append(f"  -d '{body}'")

    return " \\\n".join(lines)


def build_js_fetch(
    method: str,
    path: str,
    operation: dict,
    components: dict
) -> str:
    body = get_request_body_example(operation, components)
    protected = is_protected(operation)

    lines = []
    lines.append(f"const response = await apiFetch('{path}', {{")
    lines.append(f"  method: '{method.upper()}',")
    if body:
        lines.append(f"  body: JSON.stringify({body})")
    lines.append("});")

    if protected:
        note = "// Requires token in localStorage ('access_token')"
        lines.insert(0, note)

    return "\n".join(lines)


def group_by_tag(spec: dict) -> dict:
    groups = {}
    paths = spec.get("paths", {})
    components = spec.get("components", {})

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            tag = get_tag(operation)
            if tag not in groups:
                groups[tag] = []
            groups[tag].append((path, method, operation))

    return groups, components


def generate_markdown(spec: dict) -> str:
    groups, components = group_by_tag(spec)
    info = spec.get("info", {})

    lines = []

    # Header
    lines += [
        f"# {info.get('title', 'API')} — Frontend Integration Guide",
        "",
        "> Generated automatically from live OpenAPI spec.",
        "> Base URL: `http://127.0.0.1:8001`",
        "> Full interactive docs: http://127.0.0.1:8001/docs",
        "",
        "---",
        "",
    ]

    # Quick start
    lines += [
        "## Quick Start",
        "",
        "### JavaScript helper (copy this into your project)",
        "",
        "```javascript",
        "const BASE_URL = 'http://127.0.0.1:8001'",
        "",
        "async function apiFetch(path, options = {}) {",
        "  const token = localStorage.getItem('access_token')",
        "  const headers = {",
        "    'Content-Type': 'application/json',",
        "    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),",
        "    ...options.headers",
        "  }",
        "  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })",
        "  if (!res.ok) {",
        "    const err = await res.json()",
        "    throw new Error(err.detail || 'Request failed')",
        "  }",
        "  return res.json()",
        "}",
        "```",
        "",
        "---",
        "",
    ]

    # Language system
    lines += [
        "## Language Support",
        "",
        "All public event endpoints accept `?lang=fr` | `?lang=ar` | `?lang=tzm`",
        "",
        "- Default: `fr` if not specified",
        "- Response always returns localized `title` and `description`",
        "- Raw multilingual fields (`title_fr`, `title_ar`) are **never** in responses",
        "- Discovery endpoints use `preferred_language` from user profile automatically",
        "",
        "```",
        "GET /events/?wilaya=Bejaia&lang=ar  → title in Arabic",
        "GET /events/?wilaya=Bejaia&lang=fr  → title in French",
        "```",
        "",
        "---",
        "",
    ]

    # Caching note
    lines += [
        "## Caching Behaviour",
        "",
        "Every event list response includes header: `x-cache: HIT` or `x-cache: MISS`",
        "",
        "- `HIT` = served from Redis cache instantly",
        "- `MISS` = fetched from database",
        "- Cache invalidates automatically when admin creates/updates/deletes events",
        "- **Do NOT cache responses in the frontend** — backend cache is already optimal",
        "",
        "| Endpoint type | Cache TTL |",
        "|---|---|",
        "| Event lists | 10 minutes |",
        "| Event detail | 30 minutes |",
        "| Personalized discovery | 5 minutes |",
        "",
        "---",
        "",
    ]

    # Error handling
    lines += [
        "## Error Handling",
        "",
        "All errors follow this shape:",
        "```json",
        '{"detail": "Error message here"}',
        "```",
        "",
        "| Status | Meaning | Common cause |",
        "|---|---|---|",
        "| 400 | Bad Request | Duplicate email/username, invalid data |",
        "| 401 | Unauthorized | Missing or expired token |",
        "| 403 | Forbidden | Wrong role (user token on admin endpoint) |",
        "| 404 | Not Found | Resource doesn't exist or is deactivated |",
        "| 422 | Unprocessable | Missing required field in request body |",
        "",
        "---",
        "",
    ]

    # Endpoints by tag
    lines.append("## Endpoints\n")

    TAG_ORDER = [
        "Authentication", "Categories", "Events",
        "Users", "Eco Metrics"
    ]
    ordered_tags = TAG_ORDER + [
        t for t in groups if t not in TAG_ORDER
    ]

    for tag in ordered_tags:
        if tag not in groups:
            continue
        lines.append(f"### {tag}\n")

        for path, method, operation in groups[tag]:
            icon = get_method_color(method)
            summary = operation.get("summary", path)
            protected = is_protected(operation)
            auth_badge = " 🔒 _auth required_" if protected else " 🌐 _public_"

            lines.append(
                f"#### {icon} `{method.upper()} {path}`"
                f" — {summary}{auth_badge}\n"
            )

            desc = operation.get("description")
            if desc:
                lines.append(f"{desc}\n")

            # Query params table
            params = get_query_params(operation)
            if params:
                lines.append("**Query Parameters:**\n")
                lines.append("| Parameter | Type | Required | Description |")
                lines.append("|---|---|---|---|")
                for p in params:
                    required = "✅" if p.get("required") else "optional"
                    ptype = p.get("schema", {}).get("type", "string")
                    desc_p = p.get("description", "—")
                    lines.append(
                        f"| `{p['name']}` | {ptype} | {required} | {desc_p} |"
                    )
                lines.append("")

            # Request body
            body_example = get_request_body_example(operation, components)
            if body_example:
                lines += [
                    "**Request Body:**",
                    "```json",
                    body_example,
                    "```",
                    "",
                ]

            # Response example
            resp_example = get_response_example(operation, components)
            if resp_example:
                lines += [
                    "**Response:**",
                    "```json",
                    resp_example,
                    "```",
                    "",
                ]

            # Curl example
            curl = build_curl(method, path, operation, components)
            lines += [
                "**curl:**",
                "```bash",
                curl,
                "```",
                "",
            ]

            # JS fetch example
            js = build_js_fetch(method, path, operation, components)
            lines += [
                "**JavaScript:**",
                "```javascript",
                js,
                "```",
                "",
                "---",
                "",
            ]

    # Wilaya reference
    lines += [
        "## Wilaya & Postal Code Reference",
        "",
        "| Wilaya | Postal Code |",
        "|---|---|",
        "| Bejaia | 06000 |",
        "| Setif | 19000 |",
        "| Alger | 16000 |",
        "| Tizi Ouzou | 15000 |",
        "| Oran | 31000 |",
        "| Constantine | 25000 |",
        "",
        "> Real deployment will cover all 58 wilayat.",
        "",
        "---",
        "",
    ]

    # Checklist
    lines += [
        "## Frontend Developer Checklist",
        "",
        "1. Open http://127.0.0.1:8001/docs — confirm API is running",
        "2. `POST /auth/user/register` — create a test account",
        "3. `POST /auth/user/login` — get token, store in localStorage",
        "4. `GET /categories/` — load categories for dropdowns",
        "5. `GET /events/?lang=fr` — load all events",
        "6. `GET /events/?wilaya=Bejaia&lang=fr` — filter by location",
        "7. `POST /users/me/favourites/1` — add a favourite category",
        "8. `GET /users/me/events/discover/wilaya?wilaya=Bejaia` — personalized feed",
        "9. `POST /users/me/events/1` — register for an event",
        "10. `POST /auth/admin/login` (slug: `admin_odej`, pass: `Admin2026!`)",
        "11. `POST /events/` with `input_language: fr` — Arabic auto-fills",
        "",
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    print("📡 Fetching OpenAPI spec from running server...")
    spec = fetch_openapi()
    print(f"✅ Got spec: {len(spec.get('paths', {}))} paths found")

    print("📝 Generating FRONTEND_API_GUIDE.md...")
    markdown = generate_markdown(spec)

    OUTPUT_FILE.write_text(markdown, encoding="utf-8")
    print(f"✅ FRONTEND_API_GUIDE.md generated ({len(markdown)} chars)")
    print(f"📄 Saved to: {OUTPUT_FILE}")
