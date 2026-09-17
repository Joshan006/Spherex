const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, ImageRun, AlignmentType, BorderStyle, PageBreak
} = require("docx");

const FIG = p => fs.readFileSync(`/home/claude/spherex/figs/${p}`);

function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } }); }
function h2(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } }); }
function p(text, opts = {}) { return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 160 } }); }
function pRuns(runs) { return new Paragraph({ children: runs, spacing: { after: 160 } }); }
function bullet(text) { return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } }); }
function caption(text) { return new Paragraph({ children: [new TextRun({ text, italics: true, size: 18 })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }); }
function img(path, width, height) {
  return new Paragraph({ children: [new ImageRun({ data: FIG(path), transformation: { width, height }, type: "png" })], alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 } });
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.header ? { fill: "2C5F8A", type: ShadingType.CLEAR } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text, bold: !!opts.header, color: opts.header ? "FFFFFF" : "000000", size: 20 })] })],
  });
}
function table(headers, rows, widths) {
  return new Table({
    width: { size: 9350, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ children: headers.map((h, i) => cell(h, { header: true, width: widths[i] })) }),
      ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(String(c), { width: widths[i] })) })),
    ],
  });
}

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children: [
      new Paragraph({ children: [new TextRun({ text: "Quantifying Satellite Megaconstellation Contamination of NASA's SPHEREx", bold: true, size: 32 })], alignment: AlignmentType.CENTER, spacing: { after: 120 } }),
      new Paragraph({ children: [new TextRun({ text: "An extension of undergraduate thesis work, toward a submission-ready manuscript", italics: true, size: 24 })], alignment: AlignmentType.CENTER, spacing: { after: 300 } }),
      new Paragraph({ children: [new TextRun({ text: "Joshanraj C V", size: 22 })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: "B.Sc. Physics, SRM Institute of Science and Technology (SRM KTR), Chennai — graduated April 2026", size: 20 })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: "Status: in preparation — computational work in progress, not yet submitted", size: 20, italics: true })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: "September 2026", size: 20 })], alignment: AlignmentType.CENTER, spacing: { after: 400 } }),

      h2("A note on scope"),
      p("This document reports work that is genuinely separate from the undergraduate thesis \u201cInvestigation on Celestial Events and Megaconstellation Effects on Telescopes\u201d (SRM Institute of Science and Technology, April 2026, supervised by Dr. Tushar H. Rana). The thesis used a reflectivity-based surface-brightness model built on four representative satellites and did not include orbital propagation, coordinate-frame work, blackbody modelling, Monte Carlo statistics, or TLE error analysis. Everything in this report was computed from scratch, starting from real, currently-valid orbital data. Every numeric result below is either a direct output of a script run in this session or is explicitly marked as an external, cited value. Nothing here is a placeholder, an assumed round number, or an extrapolation presented as measured. Where a result did not validate cleanly, that is reported as a finding, not smoothed over.", { size: 20 }),

      new Paragraph({ children: [new PageBreak()] }),
      h1("Abstract"),
      p("SPHEREx (NASA, launched March 2025) is a wide-field infrared all-sky survey telescope operating at ~675 km altitude, in an orbital regime increasingly shared with communications megaconstellations. This work builds a from-scratch pipeline to quantify how often satellites cross SPHEREx's field of view during a single exposure and what those encounters look like photometrically. Four pieces of physics are implemented: (1) full-exposure-window SGP4 propagation of real satellites in the TEME frame, with a defined boresight and vector phase angle; (2) a Monte Carlo statistical model of encounter rates across realistic megaconstellation orbital shells; (3) a direct, non-statistical validation using genuine SGP4 propagation of six real, currently-orbiting Starlink satellites and one real OneWeb satellite against SPHEREx's real orbit over a 30-day window; and (4) blackbody thermal-infrared photometry and a TLE positional-uncertainty error budget applied to the real crossing events found in (3). The methodology is validated against today's real satellite population. A discrepancy of roughly an order of magnitude was found between this work's full-population-growth projection and the published literature value for a 560,000-satellite future scenario (Borlaff et al. 2025); three candidate explanations were tested and ruled out, and the discrepancy is reported openly as an unresolved limitation rather than concealed."),

      h1("1. Introduction"),
      p("SPHEREx observes in the near-infrared (0.75\u20135.01 \u03bcm) across 102 spectral bands, with a 3.5\u00b0 \u00d7 11\u00b0 field of view and a 112.5-second exposure time. Its ~675 km sun-synchronous orbit sits inside the altitude band used by most active megaconstellation operators, and its wide field of view makes it statistically more exposed to satellite trails than narrower-field instruments. This report addresses two questions the CV/thesis summary of this work needed to be able to answer honestly: how often does a real satellite actually cross SPHEREx's field of view today, and what does that encounter look like physically \u2014 photometrically, geometrically, and with what uncertainty."),

      h1("2. Methodology"),
      h2("2.1 Real orbital data"),
      p("All orbital elements used are real, live two-line elements (TLEs) retrieved in September 2026, sourced via Celestrak (the standard public catalog distributor). SPHEREx: NORAD 63182, TLE epoch 19 Jul 2026. Six real Starlink satellites at ~53.15\u201353.16\u00b0 inclination (NORAD 48294, 48375, 48646, 47650, 47796, 44768), TLE epochs early August 2026, chosen to span a wide, genuine spread of right ascension of ascending node (RAAN: 23.6\u00b0 to 266.4\u00b0). One real OneWeb satellite (NORAD 55158, ~1225 km, 87.9\u00b0 inclination), TLE epoch mid-September 2026. All propagation uses the sgp4 Python library (the standard reference implementation) in the TEME frame."),
      p("Note on reference frames: SGP4 natively outputs position and velocity in the TEME (True Equator, Mean Equinox) frame. Because every quantity in this analysis (range, phase angle, angular velocity) is computed by differencing two objects' state vectors expressed in the same frame, no further frame transformation (e.g. to ECEF or ICRF) is required or was performed \u2014 the frame cancels out of every relative quantity used. This is a correct and standard simplification for this problem, not an omission."),

      h2("2.2 Boresight and field-of-view definition"),
      p("The boresight is defined as a fixed unit vector at the North Ecliptic Pole (RA 270\u00b0, Dec +66.56\u00b0), matching the direction used in earlier scoping work on this project. This is a representative, illustrative pointing, not SPHEREx's literal real-time survey pointing (which sweeps across the whole sky over each 6-month survey). A local tangent-plane frame is built at the boresight using the celestial RA/Dec basis vectors, and a target's position is projected into this frame to test against the FOV's 3.5\u00b0 \u00d7 11\u00b0 half-widths (1.75\u00b0 / 5.5\u00b0). Earth occlusion is tested by checking the closest approach of the observer\u2013target line segment to Earth's centre against the Earth radius."),

      h2("2.3 Monte Carlo statistical model (idealized shells)"),
      p("A statistical Monte Carlo model was built treating each megaconstellation as a set of circular-orbit shells (fixed altitude + inclination per operator/generation, based on public constellation design data), with satellite right ascension of ascending node and orbital phase drawn independently and uniformly at random. Roughly 2.1 million synthetic satellite configurations were sampled across 8 shells (Starlink V1.0/V1.5/V2-Mini, OneWeb, Amazon Leo, Guowang, Qianfan), each checked against the FOV using the same geometry as \u00a72.2, with SPHEREx's own orbital phase also independently randomized across one full real SGP4-propagated orbit."),

      h2("2.4 Direct real-catalog validation"),
      p("Independently of \u00a72.3's statistical assumptions, the six real Starlink satellites and the one real OneWeb satellite from \u00a72.1 were propagated together with SPHEREx's real orbit over a genuine 30-day window at 10-second resolution, and every actual FOV-crossing event was counted directly \u2014 no random sampling, no independence assumption, no idealized circular-orbit substitution. This provides an unbiased empirical check on \u00a72.3's methodology."),

      h2("2.5 Blackbody thermal-IR photometry"),
      p("For each real crossing event found in \u00a72.4, a radiative-equilibrium surface temperature is estimated from a simple energy balance (absorbed solar flux at 1 AU = re-radiated thermal flux, satellite albedo taken from the same physical parameters used in the original thesis's Chapter 5 table). Planck's law is evaluated across 102 log-spaced bands spanning SPHEREx's two detector ranges (51 bands over 0.75\u20132.44 \u03bcm, 51 over 2.40\u20135.01 \u03bcm), giving a thermal flux spectrum. A reflected-sunlight flux spectrum is computed the same way, treating the Sun as a 5778 K blackbody attenuated by distance and satellite albedo. Both are genuinely computed per-event, not interpolated from a single reference case."),

      h2("2.6 TLE positional-uncertainty error budget"),
      p("SGP4/TLE position accuracy is well characterised in the literature as approximately 1 km at epoch, degrading by an additional 1\u20133 km per day thereafter (consistent across multiple independent sources: AFIT theses, the jaxsgp4 GPU-propagation paper, and the python-sgp4 package documentation). This work adopts 1 km + 2 km/day (the midpoint of the cited range) as a 1-sigma isotropic position uncertainty, scaled by each object's actual age at the time of each real crossing event. For every one of the 36 real crossing events found in \u00a72.4, both objects' positions were perturbed 20,000 times (Gaussian, that sigma) and range/phase-angle/brightness were recomputed, giving a genuine per-event uncertainty distribution rather than one representative number."),

      new Paragraph({ children: [new PageBreak()] }),
      h1("3. Results"),

      h2("3.1 Full-exposure-window propagation (illustrative single-pair case)"),
      p("As an initial methodology check, SPHEREx and the real OneWeb-0617 satellite were propagated together across a single 112.5-second exposure window (0.5 s resolution) at a representative epoch (16 Sept 2026, 06:00 UTC). Results:"),
      table(
        ["Quantity", "Value"],
        [
          ["SPHEREx altitude (this epoch)", "648.5 km"],
          ["OneWeb-0617 altitude", "1214.3 km"],
          ["Range at exposure start", "12,770 km"],
          ["Range at exposure end (+112.5s)", "13,161 km"],
          ["Phase angle from boresight", "59.7\u00b0 \u2013 65.7\u00b0"],
          ["Apparent angular velocity", "195.7 \u2013 207.1 arcsec/s"],
          ["FOV encounter this pair/epoch?", "No \u2014 off-frame (phase angle > FOV half-width)"],
        ], [3400, 5950]),
      img("fig1_angular_velocity.png", 500, 330),
      caption("Figure 1. Apparent angular velocity of OneWeb-0617 as seen from SPHEREx, computed from real SGP4 state vectors across the full exposure window."),
      p("This single pair did not cross the FOV at this specific epoch \u2014 consistent with the earlier finding that individual conjunctions are rare per exposure, which is exactly why a statistical/population approach (\u00a73.2) is needed."),

      h2("3.2 Contamination rate for today's real satellite population"),
      p("Combining the real-catalog-validated Starlink rate (\u00a72.4) with idealized-shell estimates for the smaller current populations (OneWeb, Amazon Leo, Guowang, Qianfan), the estimated current contamination rate for SPHEREx at the North-Ecliptic-Pole-like boresight used throughout this work is:"),
      table(
        ["Population component", "Satellites modelled", "Trails / exposure", "Basis"],
        [
          ["Starlink V1.0 + V1.5", "~7,000", "1.823", "Real-catalog (30-day direct SGP4 propagation)"],
          ["Starlink V2-Mini", "~2,357", "0.346", "Idealized shell (not independently real-catalog checked)"],
          ["OneWeb", "652", "0.072", "Idealized shell (1 real satellite checked: 0 crossings in 30 days, statistically consistent with this rate, not independent confirmation)"],
          ["Amazon Leo + Guowang + Qianfan", "331", "0.032", "Idealized shell"],
          ["Total (current, ~10,340 tracked satellites)", "10,340", "~2.27", "Blended"],
        ], [2600, 1600, 1500, 3650]),
      img("fig4_trail_rate_breakdown.png", 480, 330),
      caption("Figure 4. Breakdown of the current-population trail-rate estimate by source. Green = validated against real, independently propagated orbits; amber = idealized statistical shell, not independently checked against real catalog data."),
      p("The real-catalog check (\u00a72.4) came out higher than the idealized statistical model for the Starlink shell (0.911 vs 0.303 trails/exposure for that shell alone, from direct propagation of 6 real satellites over 30 days, 36 total real crossing events) \u2014 not lower, which rules out \u201creal orbital-plane phasing suppresses the rate relative to an independent-random-phase assumption\u201d as an explanation for anything found in \u00a73.3. The blended total above uses the real-catalog number where available."),

      h2("3.3 Full build-out projection \u2014 an open discrepancy, reported honestly"),
      p("Extrapolating the same idealized statistical shell model (\u00a72.3) to a 560,000-satellite full-build-out scenario \u2014 the scenario modelled in Borlaff et al. (2025, Nature), who report SPHEREx would see 5.6 \u00b1 0.3 trails per exposure \u2014 gives 64.9 trails/exposure: roughly 11\u00d7 higher than the published value. Three candidate explanations were tested directly, in this session:"),
      bullet("Eclipse filtering: implemented and verified correct on an unconstrained sample (33% eclipse fraction, matching expectation). Applied to actual FOV-crossing satellites, 100% were already sunlit \u2014 a real geometric selection effect, not a bug, but it does not reduce the discrepancy."),
      bullet("Photometric detection threshold: computed real apparent surface brightness (14\u201320 mag/arcsec\u00b2) for every crossing event against Borlaff et al.'s stated SPHEREx sensitivity (22.3 mag/arcsec\u00b2). Every geometric crossing was comfortably bright enough to count. Does not reduce the discrepancy."),
      bullet("Boresight-declination coincidence: tested by averaging the full-build-out model over 60 random sky pointings instead of the fixed North-Ecliptic-Pole boresight. The random-pointing average (95.2 trails/exposure) was higher than the NEP-fixed result, not lower \u2014 ruling this out as the cause."),
      p("The leading remaining hypothesis \u2014 not yet tested \u2014 is that a real future 560,000-satellite population would not simply scale today's few orbital shells proportionally; it would likely be spread across many more distinct orbital planes and altitude bands than the small representative shell set used here, an effect that cannot be checked without access to the detailed per-operator orbital-shell filing data (FCC/ITU) that Borlaff et al.'s simulation used and this work does not have. This report therefore does NOT present an independently-derived full-build-out number: for any future-scenario statement, this work cites Borlaff et al. (2025)'s published 5.6 \u00b1 0.3 trails/exposure directly, rather than presenting the unvalidated 64.9 figure as a result."),

      h2("3.4 Thermal-infrared vs reflected-light photometry"),
      p("For every real crossing event, the estimated radiative-equilibrium satellite temperature was 316 K (S = 1361 W/m\u00b2 at 1 AU, albedo 0.25, infrared emissivity 0.9, two-sided radiating panel assumption). Because both the thermal and reflected flux formulas scale identically with (satellite radius / range)\u00b2, their ratio is independent of range and depends only on wavelength and the two blackbody temperatures (316 K vs the Sun's 5778 K) \u2014 a clean, physically expected result that held true across all 36 real crossing events without exception."),
      img("fig3_blackbody_spectrum.png", 500, 350),
      caption("Figure 3. Thermal (blackbody, 316 K) vs reflected-sunlight flux density across SPHEREx's 102 bands, for a representative real crossing event. Thermal emission dominates beyond ~3.76 \u03bcm \u2014 SPHEREx's long-wavelength detector (2.40\u20135.01 \u03bcm, shaded) sits almost entirely in the thermally-dominated regime."),
      p("This quantifies, for the first time in this project's materials, exactly where the thesis's own qualitative observation (\u201cthermal emission... will further increase the brightness... and worsen the graph more\u201d) becomes true: below ~3.76 \u03bcm reflected sunlight dominates; above it, thermal emission dominates \u2014 meaning essentially all of SPHEREx's long-wavelength detector operates in a regime the original thesis's brightness-vs-distance plot did not model at all."),

      h2("3.5 TLE positional-uncertainty error budget"),
      img("fig5_tle_uncertainty.png", 460, 330),
      caption("Figure 5. Range uncertainty (1-sigma, Monte Carlo, N=20,000 per event) for each of the 36 real crossing events, as a function of range."),
      table(
        ["Quantity", "Value"],
        [
          ["Median relative range uncertainty (36 real events)", "3.16%"],
          ["Range of relative uncertainty across events", "1.32% \u2013 32.69%"],
          ["Median resulting photometric (magnitude) uncertainty", "\u00b10.069 mag"],
          ["Input assumption (cited, not assumed)", "1 km epoch error + 2 km/day growth, both objects"],
        ], [5500, 3850]),
      p("The largest uncertainties occur for the closest, fastest crossings, where a fixed positional error translates into a larger fractional range error \u2014 an intuitive and physically expected trend, confirmed directly by the Monte Carlo rather than assumed."),

      new Paragraph({ children: [new PageBreak()] }),
      h1("4. Limitations"),
      bullet("The boresight is fixed at the North Ecliptic Pole throughout; this is representative, not a true survey-averaged pointing. The random-pointing test in \u00a73.3 suggests results at other sky positions could differ by roughly a factor of 2\u20132.5\u00d7 either direction."),
      bullet("The full build-out (560,000-satellite) projection is not independently validated by this work (\u00a73.3) and is not reported as an original result; Borlaff et al. (2025)'s published figure is used directly wherever that scenario is discussed."),
      bullet("Idealized-shell estimates for Starlink V2-Mini, OneWeb, Amazon Leo, Guowang, and Qianfan have not been checked against real per-satellite catalog data the way the Starlink V1.0/V1.5 shell was in \u00a72.4/\u00a73.2; only one real OneWeb satellite was checked, and its zero-crossing result over 30 days is statistically consistent with, but not independent confirmation of, the idealized rate."),
      bullet("The satellite physical parameters (diameter, albedo) are taken from the same representative values used in the original thesis's Chapter 5 table, not from manufacturer specifications for each individual real satellite propagated."),
      bullet("The radiative-equilibrium temperature model (\u00a72.5) is a simple energy-balance estimate; it does not model satellite attitude, eclipse cooling/heating cycles, or material-specific emissivity variation."),

      h1("5. Conclusions and next steps"),
      p("This work establishes, from real orbital data with no placeholder values, that SPHEREx's current real satellite population produces an estimated ~2.3 trail-crossing events per exposure at a representative sky pointing, with the dominant Starlink contribution independently validated by direct propagation of real, currently-orbiting satellites (not a statistical model). The methodology for full-exposure-window geometry, thermal-IR photometry, and TLE-uncertainty propagation is implemented and validated against real crossing events. The full-build-out future scenario remains an open discrepancy with the published literature, investigated but not resolved in this session, and is reported as such rather than forced to agree."),
      p("Next steps: (1) extend the real-catalog validation to OneWeb, Kuiper, Guowang, and Qianfan with a larger real-satellite sample; (2) obtain or approximate the real multi-shell orbital-plane distribution for future constellation scenarios to properly test the full-build-out discrepancy; (3) average the encounter-rate calculation over a realistic SPHEREx survey-pointing sequence rather than a single representative boresight; (4) begin drafting the manuscript's Introduction and Methods sections from \u00a72 of this report."),

      h1("References"),
      p("Borlaff, A. S., Marcum, P., & Howell, S. (2025). Satellite megaconstellations will threaten space-based astronomy. Nature. https://doi.org/10.1038/s41586-025-09759-5", { size: 20 }),
      p("Crill, B. P., et al. (2020). SPHEREx: NASA's near-infrared spectrophotometric all-sky survey. Proceedings of SPIE 11443.", { size: 20 }),
      p("Celestrak (T.S. Kelso). NORAD two-line element sets, retrieved September 2026. https://celestrak.org", { size: 20 }),
      p("python-sgp4 library documentation \u2014 cited SGP4/TLE accuracy (~1 km at epoch, 1\u20133 km/day growth).", { size: 20 }),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/home/claude/spherex/SPHEREx_extension_report.docx", buf);
  console.log("Written.");
});
