---
name: typosquatting-homoglyphs
description: >-
  Detect lookalike domains, typosquatting, and Unicode homoglyph attacks
  (IDN/punycode, Cyrillic-Latin confusables, edit distance) offline without
  making network requests. Use when implementing or testing domain/URL lexical
  analysis in `ml/`.
---

# Typosquatting & Homoglyph Detection

Offline lexical analysis of domains extracted from chat messages and emails. Network-based checks (WHOIS, SSL, redirects) belong to `sec/` — this skill covers pure string/ML signals in `ml/`.

## Detection Signals

1. **IDN / Punycode & Confusables:**
   - Decode `xn--` punycode domains to Unicode (`idna`).
   - Flag mixed-script labels (e.g., Cyrillic `а`, `е`, `о`, `р`, `с`, `х` mixed with Latin) and map confusables to canonical ASCII skeleton.
2. **Visual & Edit Similarity:**
   - Compare domain (registrable domain / SLD) against a protected brand/corporate allowlist using normalized Damerau-Levenshtein distance and common visual substitutions (`rn` -> `m`, `vv` -> `w`, `0` -> `o`, `1` -> `l`/`i`).
   - Ignore exact matches to the official domain itself (`distance == 0` and no confusables = legitimate).
3. **Structural Lexical Features:**
   - Excessive subdomains, hyphen count, digit-for-letter substitutions, misleading brand name in subdomain (`paypal.com.evil-domain.tld`), suspicious TLDs.

## Constraints

- **Zero network I/O:** Never resolve DNS, fetch URLs, or follow redirects inside `ml/` (SSRF risk and latency). Operate strictly on parsed strings (`urllib.parse` / `tldextract` with offline suffix list).
- **Explainable output:** Return which brand was mimicked and which technique triggered (e.g., `homoglyph:xn--...`, `typosquatting:paypa1.com ~ paypal.com`).

## Verification

- Test against a unit suite containing: exact official domains (must score 0), punycode homoglyphs, `rn`/`m` substitutions, subdomain spoofing, and benign lookalikes.
