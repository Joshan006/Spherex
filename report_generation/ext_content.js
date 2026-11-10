// Sections 6-9 of the combined project report; also reused as the body of the standalone extension report.
module.exports = function (H) {
  const { h1, h2, p, bullet, caption, img, table, R } = H;
  const { Paragraph, PageBreak } = require("docx");
  return [
  h1("6. Extended Methodology: Real Orbital Data"),
  p("Sections 6–9 report a new extension, built independently of §5. Every number is either printed by a script in the accompanying repository (github.com/Joshan006/Spherex; script named in brackets) or is an explicitly cited external value. Superseded earlier scripts are kept separately in scripts/superseded for the record. An independent review of the code identified several errors that are corrected here (§7.2)."),

  h2("6.1 Real orbital data"),
  p("Orbital elements are real two-line element sets (TLEs) from the public NORAD catalogue (Celestrak, via KeepTrack), retrieved September 2026; every line passes the TLE checksum. SPHEREx: NORAD 63182 (epoch 19 Jul 2026). OneWeb-0617: NORAD 55158 (~1,220 km, 87.9°; epoch 15 Sep 2026). Propagation uses the reference sgp4 library in the TEME frame; all derived quantities are differences of state vectors in the same frame. Where orbits are propagated months from their TLE epoch (§6.4), SGP4 does not predict where a satellite will actually be; it provides physically consistent reference orbits (altitudes stay stable to within a few km over a year), which is what a statistical comparison requires."),

  h2("6.2 Pointing and field-of-view model"),
  p("SPHEREx's survey rules (Borlaff et al. 2025, Methods) are applied directly. For each simulated exposure, SPHEREx's position is drawn from one real SGP4-propagated orbit at the chosen date; a boresight is drawn uniformly in solid angle within 35° of local zenith (the outward radial direction at SPHEREx) and redrawn until it is at least 91° from the Sun. Over the year the angle between zenith and the Sun ranges from about 60° to 120°, and a valid pointing is found at every sampled orbital phase on every date. The 3.5° × 11.3° field (Crill et al. 2024) is centred on the boresight with a random roll, fixed inertially during the exposure. A satellite counts as a trail if, at any instant of the 112.5 s exposure, it lies inside the field, is not behind Earth, and is sunlit (cylindrical Earth shadow). The Sun direction uses the standard low-precision solar ephemeris including the equation of centre (accurate to ~0.01°). [spherex_geometry.py]"),

  h2("6.3 Constellation model and averaging"),
  p("Each constellation is modelled as circular-orbit shells (altitude and inclination from public filings) with right ascension of ascending node and orbital phase drawn uniformly at random. Shells above SPHEREx: OneWeb 1,200 km / 87.9° (6,372 filed); Guowang GW-2 ~1,145 km, split equally between 50° and 86.5° (6,912); Qianfan ~1,160 km / ~89° (~15,000 filed); Telesat Lightspeed 1,015 km / 99° (78) and 1,325 km / 50.9° (120). Below-SPHEREx control shells: Starlink 550 km / 53° and 530 km / 43°, Amazon Leo 630 km / 51.9°, Guowang GW-A59 590 km / 85°. The model is averaged over 12 dates spread across a year (Sep 2026 – Aug 2027), with 400,000 simulated exposures per shell per date and two independent random seeds: 9.6 million exposures per above-orbit shell, about 62 million in total. [13_final_model_year_averaged.py, 17_summarise_results.py]"),
  p("Time resolution matters because observable crossings are near-overhead and fast (§7.7). A convergence test on identical random draws recovers 0.58, 0.85 and 0.97 of the converged count at 7.5 s, 2.5 s and 1 s steps, with no change at 0.5 s or below. The model therefore flags candidates in a 2.5 s pass with the field padded by 4° and re-checks only those at 0.1 s; on identical draws this reproduces brute-force 0.1 s detection exactly (33 of 33 crossings). [14_convergence_test.py]"),

  h2("6.4 Real-orbit validation"),
  p("The real OneWeb-0617 orbit is propagated against the real SPHEREx orbit across twelve 30-day windows spread over a year, so that the Sun-synchronous SPHEREx plane rotates through every orientation relative to the OneWeb plane. Every 112.5 s exposure receives 20 independent random valid pointings, with the same random roll, Sun ephemeris and coarse-plus-fine detection as the model. The pooled crossing probability is compared with the idealised OneWeb shell evaluated on the same 12 dates. Because the 20 pointings share one satellite trajectory, their crossings are not independent, so the uncertainty is taken from bootstrap resampling of the twelve windows. [15_real_oneweb_validation.py]"),

  h2("6.5 Photometry and TLE error budget"),
  p("Thermal emission and reflected sunlight are computed across 0.75–5.01 μm for three surface models, because the wavelength at which they cross depends on the model: (A) a flat plate face-on to both Sun and observer; (B) a Lambertian sphere at each event's phase angle, with the flat-plate equilibrium temperature; (C) an isothermal sphere. Albedo 0.25 and emissivity 0.9 are used consistently for both the equilibrium temperature and the emitted flux. The TLE error budget takes ~1 km at epoch plus ~2 km/day (mid-range of the 1–3 km/day literature figure) as an isotropic 1-sigma error on both objects and propagates it by Monte Carlo into range and magnitude for every observable crossing, for operational TLE ages of 1, 3 and 7 days. [16_observable_events_photometry.py]"),

  new Paragraph({ children: [new PageBreak()] }),
  h1("7. Extended Results"),

  h2("7.1 Single-pair full-exposure propagation"),
  p("SPHEREx and OneWeb-0617 propagated together across one 112.5 s exposure (0.5 s steps, 16 Sep 2026 06:00 UTC) establish the geometry machinery: range 12,770 → 13,161 km, apparent angular velocity 196–207 arcsec/s, no field crossing. Individual conjunctions are rare, which is why the population approach below is needed. [01_full_window_propagation.py]"),
  img(R + "figures/fig1_angular_velocity.png", 420, 277),
  caption("Figure 7.1. Apparent angular velocity of OneWeb-0617 seen from SPHEREx across one exposure, from real SGP4 state vectors."),

  h2("7.2 How the discrepancy with the literature was found and corrected"),
  p("The first version of the model (fixed North Ecliptic Pole boresight, no survey constraints, a representative shell set scaled proportionally to 560,000 satellites) predicted 64.9 trails per exposure at full build-out, 11.5× Borlaff et al.'s 5.64. Figure 7.2 traces each step. Eclipse and brightness cuts changed nothing. Random unconstrained pointings made it worse (95.2). Applying SPHEREx's 35° zenith limit and 91° solar avoidance, which the paper's Methods specify and the first model had omitted, brought it to 11.4 and then 7.0–7.7. Correcting two constellation altitudes (Guowang and Qianfan had been placed at 800 km and 580 km; their filed shells are ~1,145 km and ~1,160 km), dropping proportional scaling, and converging the time step gave 4.5."),
  p("An independent review of the code then found that the field's roll had been effectively fixed in inertial space although the text described it as random, that the model had been evaluated on a single date, and that the time-step test had not actually varied the time step. Fixing these (random roll, 12 dates across a year, accurate Sun, the true 3.5° × 11.3° field) raised the result by about 30% to the value in §7.4. The roll correction was the largest single change."),
  img(R + "figures/fig7_investigation.png", 470, 282),
  caption("Figure 7.2. Predicted full-build-out trail rate at each stage of the investigation (log scale). Grey: superseded stages. Blue: final model. Orange band: Borlaff et al. (2025)."),
  p("The investigation also invalidates a headline figure from the earliest version of this work, ~2.3 trails per exposure for the current population “at a representative sky pointing”. That rate came from the fixed North Ecliptic Pole boresight: at all 36 real crossings behind it the pole was 101–164° from SPHEREx's zenith, a direction SPHEREx never points, and about 80% of it came from Starlink, which SPHEREx cannot see (§7.3). The figure is withdrawn and replaced by §7.5."),

  h2("7.3 Only satellites above SPHEREx's orbit can cross its field"),
  p("With the boresight within 35° of zenith, every line of sight inside the field stays well below 90° from local vertical during the exposure, so it climbs monotonically away from Earth and can only intersect orbits higher than SPHEREx's own. The simulation confirms this: the four below-orbit control shells (Starlink 550 and 530 km, Amazon Leo 630 km, Guowang GW-A59 590 km) produced 0 crossings in about 4.8 million valid exposures. Most satellites in orbit as of September 2026 are Starlink, so most of the current satellite population is invisible to SPHEREx's survey."),

  h2("7.4 Constellation-only build-out projection"),
  table(
    ["Constellation (above SPHEREx)", "Altitude / incl.", "Filed sats", "P(cross) per sat per exposure", "Trails / exposure"],
    [
      ["OneWeb", "1,200 km / 87.9°", "6,372", "2.31 × 10⁻⁴", "1.47"],
      ["Guowang GW-2 (half)", "1,145 km / 50°", "3,456", "1.45 × 10⁻⁴", "0.50"],
      ["Guowang GW-2 (half)", "1,145 km / 86.5°", "3,456", "2.26 × 10⁻⁴", "0.78"],
      ["Qianfan", "1,160 km / 89°", "~15,000", "2.06 × 10⁻⁴", "3.09"],
      ["Telesat Lightspeed", "1,015 / 1,325 km", "198", "1.3–1.8 × 10⁻⁴", "0.03"],
      ["Total", "", "~28,500", "", "5.87 ± 0.08"],
      ["Borlaff et al. (2025)", "", "~560,000 (all altitudes)", "", "5.64 (+0.28/−0.27)"],
    ], [2300, 1700, 1500, 2150, 1700]),
  p("The two random seeds give 5.84 and 5.91; \u00b10.08 is the statistical error. This projection covers only the filed high-altitude constellations; it does not include the thousands of older satellites, rocket bodies and debris fragments already orbiting above SPHEREx (\u00a77.10). It is therefore not directly comparable with the 5.64 trails per exposure that Borlaff et al. (2025) give for their ~560,000-satellite scenario, whose number of objects above 650 km could not be read from their paper. The earlier versions of this report presented the two numbers as agreeing; that comparison is withdrawn. Within the constellation-only projection, Qianfan dominates (3.1 of 5.9): its ~15,000 figure is a filing, and with only its committed 1,296-satellite phase the total would be 3.1."),

  h2("7.5 Constellation-only rate as of September 2026 (incomplete)"),
  p("As of September 2026, three constellations have satellites above SPHEREx: OneWeb (654), Guowang GW-2 (186) and Qianfan (~248) (KeepTrack, Orbital Radar, Aug–Sep 2026; Guowang split evenly between its two inclinations). Together they give about 0.24 trails per exposure. This counts only those three constellations and misses most of what is actually in orbit above SPHEREx; the full-catalogue model (\u00a77.10) and the real SPHEREx images both give about 2 trails per exposure. The ~9,400 Starlink and ~200 Amazon Leo satellites contribute nothing under SPHEREx's survey geometry. [17_summarise_results.py]"),

  h2("7.6 Real-orbit validation"),
  p("The real OneWeb orbit produced 1,289 crossings in 5.53 million valid exposure-pointings over the year, a per-satellite probability of 2.33 × 10⁻⁴, against 2.31 × 10⁻⁴ for the idealised shell on the same dates: real/model = 1.01, with a 68% bootstrap interval of 0.62–1.37. The rate varies strongly from window to window (0.8 to 11.7 per 10⁴ exposures) as the relative orbital-plane geometry rotates; a single November window contributes about 40% of all crossings, which is why the interval is wide. The idealised-shell model is therefore validated to roughly ±35%, not better."),
  img(R + "figures/fig6_observable_crossings.png", 470, 183),
  caption("Figure 7.3. Left: range at closest approach for the 1,289 observable real OneWeb crossings. Right: crossing rate in each 30-day window of the one-year real-orbit comparison, with the year means of the real orbit (solid) and the idealised shell (dashed)."),

  h2("7.7 What an observable crossing looks like"),
  table(
    ["Quantity (1,289 observable crossings)", "Value"],
    [
      ["Range at closest approach", "median 640 km (5–95%: 578–704 km)"],
      ["Apparent angular rate", "median 1.19°/s"],
      ["Time inside the field", "median 3.4 s (5–95%: 0.6–13.4 s) of a 112.5 s exposure"],
      ["Sun–satellite–SPHEREx phase angle", "median 80° (5–95%: 48–90°)"],
    ], [4400, 4950]),
  p("Because only higher satellites are visible and SPHEREx looks nearly straight up, crossings happen close to the minimum possible range (1,200 − 650 ≈ 550 km). They are close and fast, and because SPHEREx always points at least 91° from the Sun, the satellites are seen at phase angles of 90° or less (partly to fully lit faces)."),

  h2("7.8 Thermal-infrared versus reflected light"),
  p("The wavelength beyond which a satellite's own thermal emission outshines reflected sunlight lies between 3.4 and 4.1 μm, depending on the surface model: 3.81 μm for a face-on flat plate at its 316 K equilibrium temperature, 3.39 μm (median over events) for Lambertian-sphere reflection at the observed phase angles with the plate temperature, and 4.12 μm for an isothermal sphere at 266 K. In every case SPHEREx's longest-wavelength band (4.41–5.01 μm) is thermally dominated, a regime the original reflectance model (§5) could not describe and where surface darkening does not help."),
  img(R + "figures/fig3_blackbody_spectrum.png", 440, 291),
  caption("Figure 7.4. Thermal and reflected flux across SPHEREx's wavelength range for a OneWeb-size satellite at the median observable range, for the surface models in §6.5. The shaded band marks the range of crossover wavelengths."),

  h2("7.9 TLE error budget"),
  table(
    ["TLE age (per object)", "1-sigma position", "Median range uncertainty", "Median magnitude uncertainty"],
    [
      ["1 day", "3 km", "0.66%", "0.014 mag"],
      ["3 days", "7 km", "1.55%", "0.034 mag"],
      ["7 days", "15 km", "3.32%", "0.072 mag"],
    ], [2200, 2000, 2550, 2600]),
  p("With TLEs refreshed every few days, as is operationally normal, predicted trail positions and brightnesses are good to a few percent and a few hundredths of a magnitude: enough to flag contaminated exposures, though not for sub-pixel trail masking. This budget describes operational prediction; it does not describe the months-old TLEs used as reference orbits in §6.4."),

  h2("7.10 Full-catalogue model and comparison with real SPHEREx images"),
  p("Borlaff et al. (2026) counted satellite trails by eye in 6,000 real SPHEREx images taken between May and September 2025 and found 2.18 (+0.11/\u22120.09) trails per exposure, with 73% of images affected. That measurement showed the constellation-only model above to be far too low for the present day, so the model was rebuilt on the full public satellite catalogue (CelesTrak SATCAT, retrieved 10 November 2026 through a public mirror that copies it directly from celestrak.org). Every object whose orbit reaches above 650 km and that was in orbit on the date in question is included: about 18,600 objects in mid-2025 (about 4,900 payloads, 2,000 rocket bodies and 11,700 debris fragments). Each object keeps its catalogued perigee, apogee and inclination; its node, argument of perigee and orbital phase are drawn at random, and it moves on a two-body Kepler orbit during the exposure. SPHEREx's orbit, pointing rules, field roll and crossing detection are the same as in \u00a76. Five dates (15 May to 15 September 2025) with 4 million simulated exposures each and two random seeds give 40 million exposures in total. [18_full_catalogue_model.py]"),
  p("Each crossing is converted into a mean trail surface brightness, using the catalogued radar cross-section as a proxy for the optical cross-section (type median where none is listed), a Lambertian sphere with albedo 0.2 for payloads and rocket bodies and 0.1 for debris, the actual range, Sun\u2013object\u2013SPHEREx phase angle and apparent angular rate, and a trail width of one SPHEREx pixel (6.15\u2033) averaged over the 112.5 s exposure. A trail counts as detectable if it is brighter than 24.69 mag/arcsec\u00b2, the visual detection limit Borlaff et al. (2026) measured with synthetic trails injected into SPHEREx images. [19_catalogue_brightness_and_summary.py]"),
  table(
    ["", "Payloads", "Rocket bodies", "Debris", "Total"],
    [
      ["Every object above SPHEREx (no brightness cut)", "1.94", "0.93", "2.39", "5.26 \u00b1 0.04"],
      ["Detectable trails (< 24.69 mag/arcsec\u00b2)", "1.32", "0.61", "0.16", "2.09 \u00b1 0.02"],
      ["Measured in SPHEREx images (Borlaff et al. 2026)", "", "", "", "2.18 (+0.11/\u22120.09)"],
    ], [3550, 1350, 1450, 1150, 1850]),
  img(R + "figures/fig8_full_catalogue_vs_measured.png", 470, 189),
  caption("Figure 7.5. Trails per SPHEREx exposure for May\u2013September 2025: every tracked object above SPHEREx, the subset bright enough to see, and the number counted in real SPHEREx images."),
  p("The modelled 2.09 detectable trails per exposure is within 4% of the measured 2.18. The measurement was already published when this model was built, so this is a consistency check rather than a blind prediction; the brightness-model settings (albedos, detection limit, trail width) were fixed before the runs and not adjusted to match. The \u00b10.02 is statistical only; the result is dominated by systematic uncertainty in the brightness model. Shifting the detection limit by \u00b11 mag (its convention in Borlaff et al. may differ from the one used here) gives 1.4\u20132.9, and also varying the albedo between 0.1 and 0.3 gives 0.9\u20133.4. The close agreement at the nominal values should therefore be read as consistency within roughly a factor of 1.5, not as a precise match."),
  p("Several features of the result are robust to these choices. Debris dominates the geometric count (2.4 of 5.3) but contributes little once brightness is considered (0.16), because most fragments are too small to see. Intact payloads and rocket bodies, many of them decades old (the largest named contributors are Soviet/Russian Cosmos satellites and SL-series rocket stages), produce most detectable trails. OneWeb contributes 0.15, matching the independent constellation model (652 satellites \u00d7 2.3 \u00d7 10\u207b\u2074). About half the detectable rate (1.0 of 2.1) comes from objects far beyond low Earth orbit (rocket bodies on elongated transfer orbits and geostationary satellites), which produce slow, long trails; Borlaff et al.'s model population is described as low-Earth-orbit satellites. Identifying which observed trails come from which population (for example from trail length and orientation) would test this directly."),
  p("The comparison shows that the constellation-only population used in \u00a77.4\u20137.5 missed about 90% of the trails SPHEREx actually records. The geometric result of \u00a77.3, that only objects above SPHEREx's orbit can appear, is independently stated by Borlaff et al. (2026)."),

  h1("8. Limitations"),
  bullet("The full-catalogue brightness model is simple: radar cross-section as a proxy for optical size, a Lambertian sphere with a single albedo per object type, reflected sunlight only (no thermal emission or Earthshine, which Borlaff et al. include and which would add trails, especially from objects in Earth's shadow), and a detection-limit convention that may differ from theirs. Its systematic range is roughly 0.9\u20133.4 trails per exposure."),
  bullet("Catalogue objects are given random orbital orientations; real objects in Sun-synchronous orbits are not randomly oriented relative to the Sun, and objects too small to be tracked are absent."),
  bullet("The constellation-only build-out projection (\u00a77.4) excludes existing objects and depends on how many high-altitude satellites are eventually launched, above all Qianfan (1,296 committed versus ~15,000 filed)."),
  bullet("Constellations are idealised as uniformly random circular shells rather than real Walker plane structures; the real-orbit check covers one OneWeb satellite and validates the approach to about ±35%."),
  bullet("Pointings are drawn uniformly over the accessible sky with a random roll, not from SPHEREx's actual survey sequence and scan-driven roll."),
  bullet("Guowang's inclination split and Qianfan's altitude and inclination are approximations from secondary sources; in-orbit counts come from satellite-tracking websites."),
  bullet("Photometry uses simple surface models (flat plate or Lambertian sphere) with representative size and albedo; it ignores attitude, eclipse thermal history and material-specific properties, which is why the crossover is quoted as a range."),

  h1("9. Conclusions"),
  p("SPHEREx's own survey rules are its best defence against megaconstellations. Because it only points within 35\u00b0 of zenith, every object orbiting below it, including all of Starlink and Amazon Leo, is geometrically invisible. Its exposure is set by the objects above it, and these are not only the new high-altitude constellations: thousands of older satellites, rocket bodies and debris fragments already orbit there. Modelling the full public catalogue of about 18,600 such objects gives 2.1 detectable trails per exposure for May\u2013September 2025 (systematic range roughly 0.9\u20133.4), consistent with the 2.18 counted in real SPHEREx images by Borlaff et al. (2026). Most detectable trails come from intact payloads and rocket bodies, about half of them from objects far beyond low Earth orbit; debris dominates the raw count but is mostly too faint to see."),
  p("The investigation showed how sensitive such estimates are to modelling choices. Unconstrained pointing inflated the first prediction by more than an order of magnitude; a fixed field orientation and single date lowered a later one by about a quarter; and counting only new constellations underestimated the present-day rate by about a factor of ten. Each error was caught by testing against independent evidence: the literature, an independent code review, and finally real SPHEREx images."),
  p("Next steps: identify which populations produce the trails seen in SPHEREx images (for example from trail length and orientation, separating slow distant objects from fast nearby ones); add thermal emission and Earthshine to the brightness model; replace random orbital orientations with real orbits for the brightest contributors; and project the rate forward as the high-altitude constellations are launched."),
  ];
};
