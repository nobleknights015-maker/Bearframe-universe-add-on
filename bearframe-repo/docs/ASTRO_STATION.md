# Bearframe Station

0.11.15 uses the owner-supplied Astro schematic by VoponKL
(SHA-256 07c45c0f90b58dc7124d30e32f47f4773bf8ff8a755a3f758f9335f320be1711).
The installer is for private testing. Public redistribution rights have
not been verified.

The converter reads 35,961 occupied Java blocks across a 159 × 129 × 263
region. It resolves occupied palette entries against Bedrock 1.26.60,
maps format-specific names, preserves waterlogging via the second layer,
and generates 44 bounded sparse structure sections. It translates the six
block entities without copying Java actor metadata. Bedrock handles the
destination's simulation. The original redstone timing is unverified.

Run the converter with the extracted schematic and 1.26.60 blockStates.json
from minecraft-data:

```sh
node tools/import_astro.mjs /path/to/astro.litematic /path/to/blockStates.json
python3 tools/package_current.py dist
```

Use the Station Tablet to arrive in the Main Commons. Farfield Dispatch and
Mira are on the same deck. The signed Deck Lift connects to the four
department pods: Systems, Atlas Production, Watchtower, and Visual
Production. The Commons contains eight staff, including off-shift visitors
from the five other departments. The original 17 roles retain their
dialogue and services. The Return Desk restores the player's own surface
berth. A new set of saved markers keeps existing stations and return
berths usable without rebuilding the new station on later visits.

Verified geometry connectivity covers all staff and access to both lifts
and the desk. Dedicated Server verified cold construction, 44 sections,
22 staff claims, two concurrent arrival requests, repeat transit and
independent returns using entity-backed player fixtures. It did not test
client rendering or performance on Android.
