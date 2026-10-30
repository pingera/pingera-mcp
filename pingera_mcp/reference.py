"""Reference material for the model: check parameters, alert conditions and channel configuration.

Served by the `get_reference` tool and as MCP resources, and used in tool argument descriptions.
"""

from __future__ import annotations

CHECK_PARAMETERS_SHORT = (
    "Type-specific settings. Common keys: 'regions' (list of region IDs or aliases from list_check_regions; "
    "default 'RU, Moscow') and 'multi_region_execution' ({'enabled': true, 'execution_mode': 'all' | 'random_n', "
    "'count': N}). web/api: 'http_request' {method, headers, body, username, password}, 'search_text'. "
    "tcp: 'send_text', 'search_text'. ssl: 'assertions' {ssl_score, expiration_threshold}. "
    "synthetic/multistep: 'pw_script' (Playwright test source). icmp: probe_count, ip_version, assertions.max_packet_loss. "
    "dns: record_type, dns_servers, expected_answers, validation_mode, whois_lookup. portscan: ports, scan_type, assertions. "
    "Call get_reference('check_types') for the full reference."
)

CHECK_TYPES = """\
# Pingera check types and their `parameters`

Every check has `name`, `type`, a target (`url` for web/api/synthetic/multistep, `host` (+ `port`) for tcp/ssl/icmp/dns/portscan),
a schedule (`interval` in seconds, minimum 30, or `scheduling_type: "cron"` with `cron_schedule`, evaluated in the organization's
timezone) and `timeout` (seconds; max 30, synthetic 120, portscan 180).

## Common parameters
- `regions`: list of region IDs or aliases (see list_check_regions). Default: "RU, Moscow".
- `multi_region_execution`: run from several regions at once.
  `{"enabled": true, "execution_mode": "all"}` or `{"enabled": true, "execution_mode": "random_n", "count": 2}`.
  Every regional execution consumes credits.

## web, api
```json
{"http_request": {"method": "GET", "headers": {"content-type": "application/json"}, "body": "", "username": "", "password": ""},
 "search_text": "text that must be present in the response body"}
```
Methods: GET, POST, PUT, DELETE, HEAD, OPTIONS, PATCH.

## tcp
`{"send_text": "text to send", "search_text": "text expected back"}` (with `host` and `port`).

## ssl
`{"assertions": {"ssl_score": 70, "expiration_threshold": 1209600}}` - fail below the SSL score, warn N seconds before expiry.

## synthetic (browser) and multistep (API)
`{"pw_script": "<Playwright test source>"}`. Scripts use `const { test, expect } = require('@playwright/test');`.
synthetic tests get the `page` fixture (Chromium); multistep tests use the `request` fixture for HTTP calls.
Runtime: Node.js 22, Playwright 1.59, UTC timezone, 2.7 GiB memory, 1 vCPU, timeout up to 120 s (synthetic) / 30 s (multistep).
Preinstalled packages include axios, lodash, date-fns, crypto-js, jsonwebtoken, jose, otpauth, @faker-js/faker, zod, uuid, ws.
Secrets attached to the check are available as `process.env.<ENV_VARIABLE>`.

Example (multistep):
```js
const { test, expect } = require('@playwright/test');
test('API returns templates', async ({ request }) => {
  const response = await request.get('https://api.example.com/health');
  expect(response.ok()).toBeTruthy();
  expect(await response.json()).toHaveProperty('status', 'ok');
});
```

## icmp
`{"probe_count": 4, "ip_version": "auto", "probe_interval": 1.0, "probe_timeout": 1.0, "assertions": {"max_packet_loss": 10}}`
(ip_version: v4, v6 or auto).

## dns
`{"record_type": "A", "dns_servers": ["8.8.8.8"], "expected_answers": ["93.184.216.34"], "validation_mode": "contains_all", "whois_lookup": false}`
(validation_mode: contains_all or exact; whois_lookup adds domain registration/expiry info to results).

## portscan
`{"ports": "top-ports:100", "scan_type": "syn", "service_detection": true, "timing": "T3", "host_timeout": "5m",
  "assertions": {"fail_on_vulnerabilities": true, "min_risk_level": "high", "expected_open_ports": [80, 443]}}`
(scan_type: syn, connect, udp; min_risk_level: critical, high, medium, low, info).
"""

ALERT_RULE_CONDITIONS_SHORT = (
    "Extra settings for the condition: consecutive_failures takes {'count': N} (default 3); "
    "uptime_below_threshold takes {'threshold': percent (default 95), 'time_window': seconds (default 3600)}; "
    "other conditions take none."
)

ALERTS = """\
# Pingera alert rules and channels

## Rule conditions (`condition` / `condition_parameters`)
- `check_failed`: the latest run failed.
- `check_timeout`: the latest run timed out.
- `check_degraded`: the check became degraded.
- `consecutive_failures`: N runs in a row failed. `{"count": 3}` (default 3).
- `uptime_below_threshold`: uptime over a window fell below a threshold. `{"threshold": 95, "time_window": 3600}`.

Severity: low, medium, high, critical. `cooldown_period` (seconds, default 300) is the minimum time between alerts of one rule.
`auto_resolve` (default true) resolves the alert and notifies channels when the condition clears.

## Multi-region checks (`multi_region_mode`)
any_region (default), all_regions, majority, or specific_count with `multi_region_threshold: {"count": 2}`.

## Channel types and `configuration`
- email: `{"recipients": ["ops@example.com"]}`
- webhook: `{"url": "https://...", "method": "POST", "headers": {"X-Token": "..."}, "timeout": 10}` (method POST, PUT or PATCH)
- telegram: `{"chat_id": "..."}`  (start a chat with the Pingera bot to get it)
- max: `{"chat_id": "..."}`  (MAX messenger)
- sms: `{"phone_numbers": ["+79998887766"]}` (E.164)
- statuspage: `{"page_id": "...", "component_id": "..."}` - updates a status page component when alerts fire/resolve

Test notifications are supported for email, webhook, telegram and max channels.
"""

CHANNEL_CONFIGURATION_SHORT = (
    "Channel settings by type - email: {'recipients': [...]}; webhook: {'url', 'method' (POST/PUT/PATCH), 'headers', 'timeout'}; "
    "telegram/max: {'chat_id'}; sms: {'phone_numbers': ['+7...']}; statuspage: {'page_id', 'component_id'}."
)

TOPICS: dict[str, tuple[str, str]] = {
    "check_types": ("Check types and their parameters, Playwright runtime for synthetic/multistep checks", CHECK_TYPES),
    "alerts": ("Alert rule conditions, multi-region modes and alert channel configuration", ALERTS),
}
