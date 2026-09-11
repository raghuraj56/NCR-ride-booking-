# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| main    | ✅ |

This is a portfolio data-analysis project, so only the latest `main` branch
receives fixes.

## Reporting a vulnerability

Please do **not** open a public GitHub issue for security vulnerabilities.

Instead, email **raghuraj562005@gmail.com** with:

1. A description of the vulnerability
2. Steps to reproduce it (or a proof of concept)
3. Its potential impact

You should receive a response within a few days. Please avoid public
disclosure until the issue has been addressed.

## Scope notes

This project is an offline analysis pipeline — it reads a local CSV and writes
a PNG. It runs no server and processes no user input from the network, so the
attack surface is minimal. Still, reports about dependency vulnerabilities
(pandas / numpy / matplotlib), unsafe file handling, or injected data
(e.g. malicious CSV content) are welcome.
