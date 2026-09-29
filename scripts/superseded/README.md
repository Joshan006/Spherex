# Superseded scripts (kept for the record)

These are the earlier stages of the analysis, kept so the investigation in §7.2 of the
manuscript can be traced. **Do not use their numbers.** Known problems:

- 02–07: fixed North Ecliptic Pole boresight with no survey constraints (SPHEREx never points
  there at the times the crossings occur); coarse 7.5–10 s time steps; 07 contains a TLE-age sign hack.
- 08–09: first tests of the zenith and Sun constraints; wrong Guowang/Qianfan altitudes and
  proportional scaling to 560,000 satellites; 7.5 s steps.
- 10–12: field roll effectively fixed (not random, although the old text said random); single
  date / Sun position; 3.5 × 11.0° field; low-precision Sun; validation reference value hardcoded.

The final pipeline is `scripts/13`–`17` with shared geometry in `scripts/spherex_geometry.py`.
