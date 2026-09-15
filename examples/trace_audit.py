#!/usr/bin/env python3
"""Free ALPNAI Trace Audit. No credentials, redirects, retries or payments."""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    if not 0 < len(raw) <= 256000:
        raise ValueError('Input must be at most 256,000 UTF-8 bytes.')
    payload = json.loads(raw)
    if not isinstance(payload, dict) or not isinstance(payload.get('events'), list) or not 1 <= len(payload['events']) <= 1000:
        raise ValueError('Provide 1–1,000 events. See docs/en/trace-audit.md.')
    if args.report.exists():
        raise ValueError('Report exists. Select a new output path.')
    request = urllib.request.Request('https://alpnai.com/api/v1/trace-audit', data=raw, headers={'Content-Type':'application/json', 'Accept':'application/json', 'User-Agent':'ALPNAI-Trace-Audit/1.0 (+https://github.com/fredericmagnathy-ops/alpnai-agent-kit)'}, method='POST')
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
        data = response.read(2000001)
    if len(data) > 2000000:
        raise ValueError('Response exceeds the safe report size.')
    report = json.loads(data)
    if report.get('product') != 'ALPNAI Trace Audit' or report.get('payment_required') is not False:
        raise ValueError('Unexpected service response.')
    fd = os.open(args.report, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print('Audit complete. Report saved to your selected local file; no payment requested.')

if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as error:
        print(f'Service returned HTTP {error.code}; no retry or payment performed.', file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError, urllib.error.URLError):
        print('Audit could not complete. Check your input, connection and output path. No payment performed.', file=sys.stderr)
        sys.exit(1)
