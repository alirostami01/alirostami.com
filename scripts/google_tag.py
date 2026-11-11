#!/usr/bin/env python3
"""Shared Google Tag Manager constants and markup for every site page."""

CONTAINER_ID = "GTM-M3LP25QD"
SCRIPT_URL = f"https://www.googletagmanager.com/gtm.js?id={CONTAINER_ID}"
START_MARKER = "<!-- google-tag:start -->"
END_MARKER = "<!-- google-tag:end -->"


def render_google_tag(indent: str = "") -> str:
    """Return the requested Google tag snippet inside idempotence markers."""
    return "\n".join(
        (
            f"{indent}{START_MARKER}",
            f'{indent}<script async src="{SCRIPT_URL}"></script>',
            f"{indent}<script>",
            f"{indent}  window.dataLayer = window.dataLayer || [];",
            f"{indent}  function gtag(){{dataLayer.push(arguments);}}",
            f"{indent}  gtag('js', new Date());",
            f"{indent}</script>",
            f"{indent}{END_MARKER}",
        )
    )
