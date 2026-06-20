#!/usr/bin/env python3
"""Shared SSRF guard for the registry scan scripts.

Registry domains are contributor-controlled. Before a scan script issues a
request to https://{domain}/..., it must confirm the domain does not resolve to
a private, loopback, link-local, or cloud-metadata address — otherwise a
malicious registry entry can point the scanner at internal services
(169.254.169.254, localhost admin panels, RFC1918 hosts, etc.).

Usage:
    from _net_guard import is_safe_host
    if not is_safe_host(domain):
        ...skip...
"""

import ipaddress
import socket
from urllib.parse import urlsplit


def _addr_is_blocked(ip: "ipaddress._BaseAddress") -> bool:
    """True if the resolved IP falls in a range we must never connect to."""
    if (ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_multicast or ip.is_reserved or ip.is_unspecified):
        return True
    # IPv4-mapped IPv6 (e.g. ::ffff:10.0.0.1) embedding a private v4 address.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        return _addr_is_blocked(ip.ipv4_mapped)
    return False


def _host_from(domain_or_url: str) -> str:
    """Accept a bare host ('cisco.com') or a full URL and return the host."""
    if "://" in domain_or_url:
        host = urlsplit(domain_or_url).hostname or ""
    else:
        host = domain_or_url.split("/")[0].split(":")[0]
    return host.strip().rstrip(".").lower()


def is_safe_host(domain_or_url: str) -> bool:
    """Resolve the host; return False if ANY resolved address is blocked.

    Fail-closed: a resolution failure or an empty host returns False.
    """
    host = _host_from(domain_or_url)
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    if not infos:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False
        if _addr_is_blocked(ip):
            return False
    return True


def effective_url_is_safe(effective_url: str) -> bool:
    """Validate a redirect's effective URL: scheme https + public host.

    For callers that keep redirect-following and re-check the landing URL.
    """
    return urlsplit(effective_url).scheme == "https" and is_safe_host(effective_url)
