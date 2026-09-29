// Sections 6-9 of the combined manuscript; also reused as the body of the standalone extension report.
module.exports = function (H) {
  const { h1, h2, p, bullet, caption, img, table, R } = H;
  const { Paragraph, PageBreak } = require("docx");
  return [
  h1("6. Extended Methodology: Real Orbital Data"),
  p("Sections 6–9 report a from-scratch extension built independently of §5. Every number is either the direct output of a script in the accompanying repository (named in brackets) or an explicitly cited external value."),

  h2("6.1 Real orbital data"),
  p("All orbital elements are real two-line element sets (TLEs) from the public NORAD catalogue (Celestrak), retrieved September 2026. SPHEREx: NORAD 63182 (epoch 19 Jul 2026). Six Starlink satellites at ~53.16° inclination (NORAD 48294, 48375, 48646, 47650, 47796, 44768; epochs early Aug 2026) spanning RAAN 23.6–266.4°. One OneWeb satellite (NORAD 55158, ~1,200 km, 87.9°; epoch mid-Sep 2026). Propagation uses the reference sgp4 library in the TEME frame; all derived quantities are differences of state vectors in the same frame, so no further transformation is needed."),

  h2("6.2 Pointing model"),
  p("SPHEREx's survey rules (Borlaff et al. 2025, Methods) are applied directly. For each simulated exposure, SPHEREx's orbital phase is drawn from one real SGP4-propagated orbit; a boresight is drawn uniformly within 35° of local zenith (the outward radial direction at SPHEREx) and redrawn until it is at least 91° from the Sun. Because SPHEREx's orbit is terminator-aligned, the zenith direction stays 82–98° from the Sun around the whole orbit, so a valid pointing exists at every orbital phase (one is found for >99% of sampled phases). The 3.5° × 11° field is centred on the boresight with a random roll; a satellite counts as a trail if, at any instant of the 112.5 s exposure, it lies inside the field, is not behind Earth, and is sunlit. [part_g_altitude_resolved.py]"),
  p("The earliest stage of this work (§7.1–7.2) instead used a single fixed boresight at the North Ecliptic Pole with no survey constraints. That choice is retained only where it is explicitly labelled, because it turned out to be the root cause of the original discrepancy with the literature."),

  h2("6.3 Monte Carlo constellation model"),
  p("Each constellation is modelled as circular-orbit shells (altitude and inclination from public filings), with right ascension of ascending node and orbital phase drawn uniformly at random. Shells used: OneWeb 1,200 km / 87.9° (6,372 planned); Guowang GW-2 ~1,145 km, split equally between ~50° and ~86.5° (6,912); Qianfan ~1,160 km / ~89° (~15,000); Telesat Lightspeed 1,015 km / 99° (78) and 1,325 km / 50.9° (120); plus below-orbit control shells (Starlink 550/53° and 530/43°, Amazon Leo 630/51.9°, Guowang GW-A59 590/85°). Each above-orbit shell was sampled with 4 million exposures per random seed, two seeds."),
  p("Time resolution matters. Observable crossings are near-overhead and sweep the field at ~1.2°/s, so a satellite can cross the 3.5° short axis in ~3 s. A convergence test on identical random draws gave crossing probabilities of 0.61× (7.5 s step), 0.81× (2.5 s) and 0.91× (1 s) of the converged value, with no change below 0.25 s. The final model therefore flags candidates in a 2.5 s pass using a field padded by 4°, then re-checks only those at 0.1 s; on identical draws this reproduces a brute-force 0.1 s run exactly (57/57 hits). [conv_test.py, conv_check2.py]"),

  h2("6.4 Real-orbit validation"),
  p("Two independent checks use genuine SGP4 propagation of real satellites rather than idealised shells. (a) Fixed-geometry check: six real Starlink satellites against real SPHEREx over 30 days at 10 s, with the fixed NEP boresight, compared with the idealised model in the same geometry. [part_b3_real_catalog_validation.py] (b) Survey-geometry check: real OneWeb-0617 against real SPHEREx over twelve 30-day windows spread across a year (so the Sun-synchronous plane rotates through every orientation relative to the OneWeb plane), 2.5 s resolution, with 20 independent random valid pointings per exposure. [part_h_real_oneweb_constrained.py]"),

  h2("6.5 Thermal-infrared photometry"),
  p("A radiative-equilibrium temperature follows from a two-sided flat-plate energy balance (S = 1,361 W m⁻², albedo 0.25, IR emissivity 0.9): T_eq = 316 K. Planck's law is evaluated in 102 bands (51 over 0.75–2.44 μm, 51 over 2.40–5.01 μm) for the thermal term, and a 5,778 K solar spectrum scaled by albedo gives the reflected term. [part_c_full_pipeline.py, part_i_observable_events.py]"),

  h2("6.6 TLE positional-uncertainty error budget"),
  p("SGP4/TLE position error is taken as ~1 km at epoch growing by ~2 km/day (mid-range of the 1–3 km/day literature figure), applied isotropically to both objects and propagated by Monte Carlo (5,000 draws per event) into range and magnitude uncertainty for every observable crossing. Results are given for operationally realistic TLE ages of 1, 3 and 7 days. [part_i_observable_events.py]"),

  new Paragraph({ children: [new PageBreak()] }),
  h1("7. Extended Results"),

  h2("7.1 Single-pair full-exposure propagation"),
  p("SPHEREx and OneWeb-0617 propagated together across one 112.5 s exposure (0.5 s steps, 16 Sep 2026 06:00 UTC) establish the geometry machinery: range 12,770 → 13,161 km, apparent angular velocity 196–207 arcsec/s, no field crossing. Individual conjunctions are rare, which is why the population approach below is needed. [part_a_sgp4_propagation.py]"),
  img(R + "figures/fig1_angular_velocity.png", 420, 277),
  caption("Figure 7.1. Apparent angular velocity of OneWeb-0617 seen from SPHEREx across one exposure, from real SGP4 state vectors."),

  h2("7.2 How the discrepancy with the literature was found and closed"),
  p("The first version of the model (fixed NEP boresight, no survey constraints, a representative shell set scaled proportionally to 560,000 satellites) predicted 64.9 trails per exposure at full build-out — 11.5× Borlaff et al.'s 5.64. Figure 7.2 traces each step of the investigation. Eclipse and brightness cuts changed nothing (every crossing was sunlit and far above the 22.3 mag/arcsec² threshold). Averaging over random unconstrained sky pointings made it worse (95.2). Reading the paper's Methods showed that SPHEREx's 35° zenith limit and 91° solar avoidance had never been applied; applying them brought the prediction to 11.4 and then 7.0–7.7."),
  p("That intermediate 7.0–7.7 was not accepted as the answer, because checking it exposed three further problems: two shell altitudes were wrong (Guowang had been placed at 800 km and Qianfan at 580 km; their main filed shells are ~1,145 km and ~1,160 km), proportional scaling to 560,000 had inflated OneWeb to ~45,000 satellites, and the 7.5 s time step missed ~40% of the fast, near-overhead crossings (§6.3). Fixing all three gives the final result in §7.4."),
  img(R + "figures/fig7_investigation.png", 470, 247),
  caption("Figure 7.2. Predicted full-build-out trail rate at each stage of the investigation (log scale). Grey: superseded stages. Blue: final model. Orange band: Borlaff et al. (2025)."),
  p("The same investigation invalidates a headline figure reported in the earlier version of this work: ~2.3 trails per exposure for today's population “at a representative sky pointing”. That rate was computed at the fixed NEP boresight, and at all 36 real crossings behind it the NEP was 101–164° from SPHEREx's zenith — below the local horizon, a direction SPHEREx never points. Around 80% of it came from Starlink, which §7.3 shows cannot be seen at all under real pointing rules. The figure is withdrawn and replaced by §7.5."),

  h2("7.3 Only satellites above SPHEREx's orbit can cross its field"),
  p("With the boresight within 35° of zenith, even the field's far corner stays within ~41° of zenith, so every line of sight climbs monotonically away from Earth and can only intersect orbits higher than SPHEREx's own. The simulation confirms this exactly: Starlink (550 km, 530 km), Amazon Leo (630 km) and Guowang GW-A59 (590 km) produced 0 crossings in ~398,000 valid exposures each, in each of two seeds. This single fact explains most of the original discrepancy: the fixed, unconstrained NEP pointing let SPHEREx look down through the densest low shells, which its real survey never does."),

  h2("7.4 Full build-out prediction versus Borlaff et al. (2025)"),
  table(
    ["Constellation (above SPHEREx)", "Altitude / incl.", "Planned sats", "P(cross) per sat per exposure", "Trails / exposure"],
    [
      ["OneWeb Gen 1 + Gen 2", "1,200 km / 87.9°", "6,372", "1.74 × 10⁻⁴", "1.11"],
      ["Guowang GW-2 (half)", "1,145 km / 50°", "3,456", "1.41 × 10⁻⁴", "0.49"],
      ["Guowang GW-2 (half)", "1,145 km / 86.5°", "3,456", "1.70 × 10⁻⁴", "0.59"],
      ["Qianfan", "1,160 km / 89°", "15,000", "1.50 × 10⁻⁴", "2.25"],
      ["Telesat Lightspeed", "1,015 / 1,325 km", "198", "1.0–1.8 × 10⁻⁴", "0.03"],
      ["Total", "", "28,482", "", "4.46 ± 0.2"],
      ["Borlaff et al. (2025)", "", "~560,000 (all altitudes)", "", "5.64 (+0.28/−0.27)"],
    ], [2300, 1700, 1500, 2150, 1700]),
  p("The uncertainty is the spread between two independent seeds (4.29 and 4.62), larger than the formal Monte Carlo error (±0.07). The prediction is 0.79× the published value. At the mean per-satellite probability (1.57 × 10⁻⁴), matching 5.64 exactly would need ~36,000 satellites above 650 km rather than the ~28,500 whose filings could be sourced here. Borlaff et al.'s constellation registry (their Extended Data Table 1, June 2025) could not be read as data for this work, so whether it contains those ~7,500 additional high-altitude satellites is the one quantity that remains to be checked. Independently, the real-orbit validation (§7.6) bounds the model at ×(1.24 ± 0.42), giving a band of 3.7–7.4 trails per exposure that contains the published value. The discrepancy has therefore gone from 11.5× to agreement within this model's stated uncertainty, with the residual attributed to one named, checkable input."),

  h2("7.5 Today's population"),
  p("Only OneWeb (~652 satellites at 1,200 km) and the first Qianfan satellites (~108) orbit above SPHEREx today. They give ~0.13 trails per exposure — about one exposure in eight carries a trail — with OneWeb contributing ~0.11. The ~9,400 Starlink and ~200 Amazon Leo satellites currently in orbit contribute nothing under SPHEREx's real survey geometry. [part_g_altitude_resolved.py]"),

  h2("7.6 Real-orbit validation"),
  p("Survey-geometry check: the real OneWeb orbit produced 962 crossings in 5.26 million valid exposure-pointings over one year, a per-satellite probability of 1.83 × 10⁻⁴ against the idealised shell's 1.56 × 10⁻⁴ at the same 2.5 s resolution. The rate varies strongly with season (0.6 to 8.8 per 10⁴ exposures across the twelve windows) as the relative plane geometry rotates, so the honest uncertainty comes from window-to-window scatter: real/model = 1.24 ± 0.42, consistent with 1. Without the one high November window the ratio is 0.82."),
  p("Fixed-geometry check: six real Starlink satellites gave 36 crossings in 30 days (0.91 trails/exposure scaled to the shell) against 0.30 from the idealised model in the same unphysical NEP geometry. Given the >10× month-to-month variation seen above, a single 30-day window from six satellites is expected to scatter by factors of a few; this check is kept as a record but carries no weight in the final result because its geometry is not one SPHEREx observes."),
  img(R + "figures/fig6_observable_crossings.png", 470, 183),
  caption("Figure 7.3. Left: range at closest approach for the 962 observable real OneWeb crossings. Right: crossing rate in each 30-day window of the one-year real-orbit sweep, against the idealised-shell value."),

  h2("7.7 What an observable crossing looks like"),
  table(
    ["Quantity (962 observable crossings)", "Value"],
    [
      ["Range at closest approach", "median 635 km (5–95%: 578–700 km)"],
      ["Apparent angular rate", "median 1.16°/s (4,157 arcsec/s)"],
      ["Time to cross the 3.5° short axis", "~3 s of a 112.5 s exposure"],
      ["Boresight zenith angle", "≤35° at exposure start (≤41° by exposure end)"],
    ], [4400, 4950]),
  p("Because only higher satellites are visible and SPHEREx looks nearly straight up, crossings happen at almost the minimum possible range (1,200 − 650 ≈ 550 km). They are therefore close, bright and fast, rather than the distant (1,000–5,000 km) encounters that dominated the unconstrained model."),

  h2("7.8 Thermal-infrared versus reflected light"),
  p("With T_eq = 316 K, thermal emission overtakes reflected sunlight at 3.76 μm. Both terms scale identically with (satellite radius/range)², so the crossover depends only on temperature and albedo, not on geometry; it is unchanged when the analysis moves from the fixed-NEP events to the observable OneWeb crossings. SPHEREx's long-wavelength detector (2.40–5.01 μm) therefore sits largely in the thermally dominated regime that the original reflectance model (§5) could not describe, and where surface darkening does not help."),
  img(R + "figures/fig3_blackbody_spectrum.png", 440, 306),
  caption("Figure 7.4. Thermal (316 K) and reflected-sunlight flux across SPHEREx's 102 bands for a representative encounter. The crossover wavelength is independent of range."),

  h2("7.9 TLE error budget"),
  table(
    ["TLE age (per object)", "1-sigma position", "Median range uncertainty", "Median magnitude uncertainty"],
    [
      ["1 day", "3 km", "0.67%", "0.014 mag"],
      ["3 days", "7 km", "1.56%", "0.034 mag"],
      ["7 days", "15 km", "3.34%", "0.073 mag"],
    ], [2200, 2000, 2550, 2600]),
  p("Because observable crossings are close (~635 km), position errors of a few km matter more than they did for the distant fixed-NEP events. With TLEs refreshed every few days, as is operationally normal, predicted trail positions and brightnesses are good to a few percent and a few hundredths of a magnitude — sufficient for flagging contaminated exposures, though not for sub-pixel trail masking."),

  h1("8. Limitations"),
  bullet("The full-build-out prediction depends on the number of satellites filed above 650 km. Only filings that could be sourced (OneWeb, Guowang GW-2, Qianfan, Telesat) are included; Borlaff et al.'s full registry could not be read as data. This is the main remaining source of difference from the published value."),
  bullet("Constellations are idealised as uniformly random circular shells, not real Walker plane structures. The real-orbit check (§7.6) tests this for one OneWeb satellite only; its ±34% uncertainty is the model's validation limit."),
  bullet("The Guowang GW-2 inclination split (50°/86.5°) and the Qianfan inclination are approximations from secondary sources."),
  bullet("The field's roll angle is random; SPHEREx's actual roll follows its scan strategy. Survey pointings are drawn uniformly over the accessible cone rather than following the real survey sequence."),
  bullet("The Sun direction uses a low-precision ephemeris and a single epoch for the statistical model; the real-orbit sweep uses a date-dependent Sun."),
  bullet("Photometry uses a flat-plate equilibrium temperature and Lambertian reflection without a phase function, attitude, eclipse thermal history or material-specific emissivity. Satellite size and albedo are representative values, not manufacturer specifications."),

  h1("9. Conclusions"),
  p("SPHEREx's own survey rules are its best defence against megaconstellations. Because it only looks within 35° of zenith, every satellite orbiting below it — all of Starlink and Amazon Leo, today the large majority of all satellites — is geometrically invisible. Its exposure is set entirely by the smaller population of high-altitude constellations: ~0.13 trails per exposure today, rising to 4.5 ± 0.2 when the filed high-altitude constellations (chiefly Qianfan and Guowang) are complete. That is consistent with the 5.64 published by Borlaff et al. (2025) within this model's validation uncertainty, with the residual traced to a single input, the high-altitude satellite count."),
  p("The encounters that do occur are near-overhead, fast and bright, and in SPHEREx's long-wavelength bands (above ~3.76 μm) they are dominated by thermal emission that surface darkening cannot suppress. The investigation also showed how sensitive such estimates are to modelling choices: an unconstrained pointing inflated the full-build-out prediction by more than an order of magnitude and produced a current-population figure (~2.3 per exposure) that does not apply to SPHEREx at all."),
  p("Next steps: obtain the full constellation registry to close the high-altitude satellite count; extend the real-orbit validation to many OneWeb and Qianfan satellites across multiple planes; replace random pointings with SPHEREx's published survey sequence and roll; and compare predicted crossings with trails identified in public SPHEREx images."),
  ];
};
