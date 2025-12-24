#!/usr/bin/env python3
"""
Dump ChatGPT Projects ("snorlax gizmos") using a DevTools "Copy as cURL" snippet.

Usage:
  1) In Chrome DevTools Network, right-click the request:
       /backend-api/gizmos/snorlax/sidebar?...
     -> Copy -> Copy as cURL
  2) Save it to curl.txt (or pass via --curl-file)
  3) Run:
       python3 chatgpt_projects_dump.py --curl-file curl.txt

Outputs:
  - projects_raw.json  (full API responses merged)
  - projects.json      (flattened list of projects + lightweight metadata)
"""

import argparse
import json
import re
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import requests


def parse_curl(curl_text: str):
    """
    Very small parser for common "Copy as cURL" formats.
    Extracts:
      - url
      - headers dict
    """
    # Grab URL (first https://... or https://chatgpt.com/...)
    url_match = re.search(r"(https?://[^\s'\"\\]+)", curl_text)
    if not url_match:
        raise ValueError("Could not find a URL in the cURL text.")

    url = url_match.group(1)

    # Extract -H 'Header: value' and -H "Header: value"
    headers = {}
    for m in re.finditer(r"-H\s+(?:'([^']+)'|\"([^\"]+)\")", curl_text):
        header_line = m.group(1) or m.group(2)
        if ":" in header_line:
            k, v = header_line.split(":", 1)
            headers[k.strip()] = v.strip()

    return url, headers


def rebuild_url_with_params(original_url: str, params: dict):
    parsed = urlparse(original_url)
    q = parse_qs(parsed.query)

    # overwrite with given params (stringify)
    for k, v in params.items():
        if v is None:
            q.pop(k, None)
        else:
            q[k] = [str(v)]

    new_query = urlencode({k: v[0] for k, v in q.items()})
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))


def extract_projects_from_payload(payload: dict):
    items = payload.get("items", []) or []
    projects = []

    for it in items:
        # Your shape: it["gizmo"]["gizmo"] is the actual project object
        g = (it.get("gizmo") or {}).get("gizmo") or {}
        if not g:
            continue

        pid = g.get("id")                       # <-- g-p-...
        name = (g.get("display") or {}).get("name") or g.get("name") or g.get("title")

        projects.append(
            {
                "project_id": pid,
                "name": name,
                "short_url": g.get("short_url"),
                "created_at": g.get("created_at"),
                "updated_at": g.get("updated_at"),
                "last_interacted_at": g.get("last_interacted_at"),
                "num_interactions": g.get("num_interactions"),
                "memory_enabled": g.get("memory_enabled"),
                "memory_scope": g.get("memory_scope"),
                "organization_id": g.get("organization_id"),
                "author": (g.get("author") or {}).get("display_name"),
                # optional: include conversations summary already embedded in this response
                "conversations_preview": (it.get("conversations") or {}).get("items", []),
            }
        )

    return projects



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--curl-file", default="curl.txt", help="Path to file containing 'Copy as cURL' text")
    ap.add_argument("--owned-only", action="store_true", help="Force owned_only=true")
    ap.add_argument("--conversations-per-project", type=int, default=0, help="Set conversations_per_gizmo (0 is smallest)")
    ap.add_argument("--max-pages", type=int, default=50, help="Safety limit for pagination pages")
    ap.add_argument("--out-prefix", default="projects", help="Output file prefix (default: projects)")
    args = ap.parse_args()

    curl_text = open(args.curl_file, "r", encoding="utf-8").read()
    base_url, headers = parse_curl(curl_text)

    # Ensure we are hitting the sidebar endpoint (you can still paste any URL from Network)
    if "/backend-api/" not in base_url:
        print("Warning: URL doesn't look like a /backend-api/ call. Make sure you copied the right request.", file=sys.stderr)

    # Build the first URL, overriding key params to reduce payload
    params = {
        "conversations_per_gizmo": args.conversations_per_project,
    }
    if args.owned_only:
        params["owned_only"] = "true"

    next_cursor = None
    all_payloads = []
    all_projects = []
    seen_project_ids = set()

    session = requests.Session()

    for page in range(1, args.max_pages + 1):
        page_params = dict(params)
        if next_cursor:
            page_params["cursor"] = next_cursor

        url = rebuild_url_with_params(base_url, page_params)

        resp = session.get(url, headers=headers, timeout=60)
        if resp.status_code != 200:
            print(f"Request failed: HTTP {resp.status_code}", file=sys.stderr)
            print(resp.text[:2000], file=sys.stderr)
            sys.exit(2)

        payload = resp.json()
        all_payloads.append(payload)

        projects = extract_projects_from_payload(payload)
        for p in projects:
            pid = p.get("project_id")
            if pid and pid not in seen_project_ids:
                seen_project_ids.add(pid)
                all_projects.append(p)

        # Cursor / pagination fields vary; try common possibilities
        next_cursor = (
            payload.get("next_cursor")
            or payload.get("cursor")
            or payload.get("pagination", {}).get("next_cursor")
            or payload.get("data", {}).get("next_cursor")
        )

        print(f"Page {page}: +{len(projects)} (unique total: {len(all_projects)}) cursor={bool(next_cursor)}")

        if not next_cursor:
            break

    # Save raw merged payloads
    with open(f"{args.out_prefix}_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_payloads, f, indent=2)

    # Save flattened projects list (still keeps raw objects inside each entry)
    with open(f"{args.out_prefix}.json", "w", encoding="utf-8") as f:
        json.dump(all_projects, f, indent=2)

    # Print a small human summary
    print("\nProjects:")
    for p in all_projects:
        print(f"- {p.get('name') or '(no name)'}  [{p.get('project_id')}]")

    print(f"\nWrote: {args.out_prefix}_raw.json and {args.out_prefix}.json")


if __name__ == "__main__":
    main()
