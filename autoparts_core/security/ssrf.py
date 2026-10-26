"""SSRF protections for URL import and redirects."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "metadata",
}


def validate_public_url(url: str, *, allow_http: bool = True) -> tuple[bool, str]:
    if not url or not isinstance(url, str):
        return False, "empty URL"
    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "unparseable URL"

    scheme = (parsed.scheme or "").lower()
    if scheme not in (("http", "https") if allow_http else ("https",)):
        return False, f"scheme '{scheme}' not allowed"

    host = (parsed.hostname or "").lower()
    if not host:
        return False, "missing host"
    if host in BLOCKED_HOSTS or host.endswith(".localhost"):
        return False, "blocked host"
    if host.endswith(".local") or host.endswith(".internal"):
        return False, "local/internal host blocked"

    # Literal IP?
    try:
        ip = ipaddress.ip_address(host)
        if _is_blocked_ip(ip):
            return False, f"blocked IP range: {ip}"
    except ValueError:
        # Resolve DNS and check all answers
        try:
            infos = socket.getaddrinfo(host, None)
        except socket.gaierror:
            return False, "DNS resolution failed"
        for info in infos:
            sockaddr = info[4]
            try:
                ip = ipaddress.ip_address(sockaddr[0])
            except ValueError:
                continue
            if _is_blocked_ip(ip):
                return False, f"resolves to blocked IP: {ip}"

    return True, "ok"


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
        or str(ip) in {"169.254.169.254", "metadata"}
    )


def sanitize_export_cell(value: object) -> object:
    """Prevent spreadsheet formula injection."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value
