#!/usr/bin/env python3
"""Generate the wallet QR codes used on the support pages.

Each QR code encodes *exactly* the plain wallet address (no URI scheme,
no amount, no label), so scanning it in any wallet app yields the address
character-for-character.

Usage:
    pip install segno
    python3 scripts/generate-wallet-qr.py

Output: images/donate/<name>.png and .svg
"""

from pathlib import Path

import segno

OUT_DIR = Path(__file__).resolve().parent.parent / "images" / "donate"

WALLETS = {
    "bitcoin": "bc1qg7xap7ys84j6s0zj7e607whwgak4gvzttw0yew",
    "usdt-trc20": "TEL83d98uJqtVcJfttjjK7dCEB7q9g7fg",
    "ethereum": "0xD52B0e8a6244e1c155285020191199524349292f",
    "solana": "BEXuadMGmKCPJQ7ZAvB4HooYjn6psMXARzr2doeie4y9",
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, address in WALLETS.items():
        qr = segno.make(address, error="h")  # high error correction
        qr.save(OUT_DIR / f"{name}.png", scale=10, border=4, dark="#000000", light="#ffffff")
        qr.save(OUT_DIR / f"{name}.svg", scale=10, border=4, dark="#000000", light="#ffffff")
        print(f"{name}: version {qr.version}, ECC {qr.error.upper()} -> {address}")


if __name__ == "__main__":
    main()
