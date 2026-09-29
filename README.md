# NetPulse – Network Diagnostic Toolkit

NetPulse is a Python-based command-line network diagnostic toolkit designed for basic NOC, IT Support, and Network Troubleshooting tasks.

It provides quick tools for testing connectivity, resolving DNS records, tracing network routes, checking open ports, viewing system information, and saving diagnostic reports.

## Features

* Ping Test
* DNS Lookup
* Traceroute
* Port Check
* System Information
* Quick Health Check
* Save Diagnostic Report
* Structured JSON report with timestamped outcomes (v1.1)
* Distinct TCP outcomes: connected, refused, timeout, DNS error, and network error
* Simple colored CLI interface
* Cross-platform support for Windows and Linux

## Use Case

NetPulse is useful for:

* NOC Engineers
* Network Technicians
* IT Support Specialists
* Helpdesk Teams
* Students learning networking fundamentals

## Tools Included

### 1. Ping Test

Checks connectivity to a website or IP address.

### 2. DNS Lookup

Resolves a domain name to its IP address.

### 3. Traceroute

Shows the route packets take to reach a destination.

### 4. Port Check

Checks whether a specific TCP port is open or unreachable.

### 5. System Information

Displays local system and network information.

### 6. Quick Health Check

Runs a quick diagnostic test including DNS, ping, and HTTPS port check.

### 7. Save Report

Saves diagnostic results into a timestamped report file.

## How to Run

```bash
python NetPulse.py
```

## Example

```text
[1] Ping Test
[2] DNS Lookup
[3] Traceroute
[4] Port Check
[5] System Information
[6] Quick Health Check
[7] Save Report
[8] Clear Screen
[9] Exit
```

## Skills Demonstrated

* Python scripting
* Network troubleshooting
* DNS resolution
* ICMP testing
* TCP port checking
* Traceroute analysis
* CLI application design
* Technical documentation

## v1.1: evidence you can review

The TCP check now separates connection refusal, timeout, name-resolution errors,
and other network errors. A timeout alone is not labelled a closed port, and a
successful TCP connection is not presented as proof of application health.

Save Report writes both UTF-8 text and JSON. JSON includes `schema_version`,
tool version, timezone-aware timestamps, and the status/output of each check.
Command status records the command's exit result; it does not infer a root cause.

Reports can contain hostnames, IP addresses, and local system details. Keep real
operational reports private. Use only authorized endpoints for network checks.

Run the tests (Python 3.9+, no third-party dependencies required):

```bash
python -m unittest discover -s tests -v
```

The tests exercise distinct failures with mocked sockets, UTF-8 report export,
and one real connection on the local loopback interface. They do not scan external
hosts or claim validation in a production NOC. Ping/traceroute also require the
corresponding operating-system commands; DNS and TCP results have their own scope.

See [an illustrative JSON report](examples/sample-report.json). It uses a reserved
example hostname and invented timestamps; it is not a real customer incident.

### ملخص التحديث

أصبح فحص TCP يميز بين نجاح الاتصال، رفضه، انتهاء المهلة، فشل حل الاسم،
والأخطاء الشبكية الأخرى. لا تُفسَّر المهلة وحدها كدليل على إغلاق المنفذ.
يحفظ المشروع تقريرًا نصيًا ونسخة JSON بنتائج مؤرخة، لتسهيل مراجعة الفحوصات.
الاختبارات محلية، والتقرير المثال توضيحي؛ لا يتضمن بيانات عميل أو تشغيل حقيقية.

## Author

Saqer Hassan Al-Osaimi
Computer Networks & Internet Diploma
CCNA Certified
Aspiring NOC / Network Engineer
