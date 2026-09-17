const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, ImageRun, AlignmentType, PageBreak
} = require("docx");

const FIG = p => fs.readFileSync(p);

function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 150 } }); }
function h2(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } }); }
function h3(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 100 } }); }
function p(text, opts = {}) { return new Paragraph({ children: [new TextRun({ text, size: 21, ...opts })], spacing: { after: 160 } }); }
function bullet(text) { return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 }, run: { size: 21 } }); }
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
const R = "/home/claude/spherex/";

const children = [
  new Paragraph({ children: [new TextRun({ text: "Investigation of Celestial Events and Megaconstellation Effects on Space Telescopes", bold: true, size: 32 })], alignment: AlignmentType.CENTER, spacing: { after: 120 } }),
  new Paragraph({ children: [new TextRun({ text: "A Case Study of NASA's SPHEREx, with an Extended Real-Orbital-Data Analysis", italics: true, size: 24 })], alignment: AlignmentType.CENTER, spacing: { after: 300 } }),
  new Paragraph({ children: [new TextRun({ text: "Joshanraj C V", size: 22 })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
  new Paragraph({ children: [new TextRun({ text: "B.Sc. Physics, SRM Institute of Science and Technology (SRM KTR), Chennai", size: 20 })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
  new Paragraph({ children: [new TextRun({ text: "Original undergraduate project supervised by Dr. Tushar H. Rana, Department of Physics and Nanotechnology (submitted April 2026); extended analysis conducted independently thereafter", size: 18, italics: true })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
  new Paragraph({ children: [new TextRun({ text: "Status: manuscript in preparation, not yet submitted for publication", size: 20, italics: true })], alignment: AlignmentType.CENTER, spacing: { after: 300 } }),

  h1("Abstract"),
  p("Satellite megaconstellations in Low Earth Orbit increasingly overlap the operational altitudes of space telescopes, and NASA's SPHEREx \u2014 a wide-field (39.5 deg\u00b2), 102-band near-infrared all-sky survey mission launched March 2025 \u2014 is particularly exposed due to its large field of view and its 675 km sun-synchronous orbit. This work has two parts. The first is an original reflectance-based photometric model (undergraduate project, 2025\u201326) estimating satellite trail surface brightness as a function of range for four representative satellite types (Starlink V1.0/V1.5/V2-Mini, OneWeb Gen 1), building on the methodology and headline figures of Borlaff et al. (2025, Nature). The second is a from-scratch extension built on real, currently-valid orbital data: full-exposure-window SGP4 propagation, a Monte-Carlo statistical model of encounter rates across realistic megaconstellation shells, a direct validation using genuine propagation of real, currently-orbiting satellites against SPHEREx's real orbit, blackbody thermal-infrared photometry across SPHEREx's 102 bands, and a TLE positional-uncertainty error budget. The extension finds SPHEREx's current real satellite population produces an estimated ~2.3 trail-crossing events per exposure at a representative sky pointing, with the dominant contribution independently confirmed by direct propagation of real satellites rather than a statistical model, and identifies ~3.76 \u03bcm as the wavelength above which thermal emission overtakes reflected sunlight in a typical encounter. A discrepancy between this work's full-constellation-build-out projection and the published literature value (Borlaff et al. 2025) was investigated, not resolved, and is reported as an open limitation."),

  new Paragraph({ children: [new PageBreak()] }),

  h1("1. Introduction"),
  p("For decades, space telescopes were considered the definitive solution to ground-based light pollution: above the atmosphere, a telescope escapes the glow of city lights, atmospheric turbulence, and the wavelengths the atmosphere absorbs. That assumption held for roughly forty years. In May 2019, SpaceX launched its first batch of 60 Starlink satellites, and within days astronomers and photographers were reporting bright streaks across long-exposure images."),
  p("Since 2019, the number of active satellites in Low Earth Orbit has grown from roughly 2,000 to more than 15,000, and companies across the United States, Europe, and China have filed plans for over 560,000 satellites over the next decade and a half. If even partially realised, the orbital environment SPHEREx now occupies will be almost unrecognisable within its own operational lifetime."),
  p("This report documents, as clearly as possible, what the evidence says will happen to SPHEREx if current trends continue, what already has happened at today's real population (via an independent, from-scratch analysis using real orbital data), and what remains genuinely unresolved."),

  h1("2. The Rise of Satellite Megaconstellations"),
  h2("2.1 Background"),
  p("A megaconstellation is a group of hundreds to tens of thousands of satellites working toward a shared commercial goal, typically global broadband delivery from Low Earth Orbit. The concept is not new \u2014 Iridium launched 66 satellites for telephony in 1998 \u2014 but early systems were small, and launch costs were prohibitive. Reusable rockets (principally SpaceX's Falcon 9) and falling small-satellite manufacturing costs changed the economics: SpaceX's first Starlink launch in May 2019 carried 60 satellites at once, a number that quickly became routine."),
  h2("2.2 Major Operators"),
  table(
    ["Operator", "Constellation", "Active (early 2026)", "Planned total", "Altitude (km)"],
    [
      ["SpaceX (USA)", "Starlink", "~9,357", "Up to 42,000", "340\u2013614"],
      ["Amazon (USA)", "Amazon Leo (fmr. Kuiper)", "~212", "3,236 (Phase 1)", "590\u2013630"],
      ["Eutelsat/OneWeb (EU/UK)", "OneWeb Gen 1", "~652", "~6,372", "~1,200"],
      ["China (state)", "Guowang", "~29", "12,992", "500\u20131,145"],
      ["SSST (China)", "Qianfan", "~90", "~15,000", "550\u2013600"],
    ], [2400, 2400, 1750, 1750, 1050]),
  p("Starlink alone held roughly 75% of all active satellites as of December 2025. Amazon's Project Kuiper (rebranded Amazon Leo in November 2025) is ramping production at up to five satellites per day. China's Guowang (state-owned) and Qianfan (commercial) together represent a comparable future Chinese LEO infrastructure."),
  h2("2.3 Growth Trajectory"),
  p("Active LEO satellite counts grew from roughly 400 in 2000, to 2,000 at Starlink's first launch (2019), to about 15,000 by 2025 \u2014 and industry filings project roughly 100,000 by 2030 and up to 560,000 at full constellation build-out by the late 2030s. That 560,000 figure is not a worst-case hypothetical; it is what has actually been filed with regulators."),
  h2("2.4 Orbital Overlap with Astronomy"),
  p("Almost all megaconstellation satellites operate between 340 and 1,200 km altitude \u2014 precisely the band most LEO space telescopes occupy. SPHEREx orbits at 675 km; Hubble at ~540 km; China's planned Xuntian telescope at 400\u2013450 km. This overlap is not accidental: Low Earth Orbit is where internet satellites need to be for competitive signal latency (a 550 km satellite has under 30 ms round-trip delay, versus ~600 ms from geostationary orbit)."),
  p("Any LEO satellite, warmed by the Sun, radiates thermally in the infrared \u2014 a mechanism reflective-surface darkening (used to mitigate optical brightness for ground-based astronomers) does essentially nothing to address, since thermal emission is a function of temperature, not surface colour."),

  h1("3. The SPHEREx Mission"),
  h2("3.1 Overview and Science Goals"),
  p("SPHEREx (Spectro-Photometer for the History of the Universe, Epoch of Reionization, and Ices Explorer) launched 11 March 2025 on a Falcon 9 from Vandenberg Space Force Base, managed by JPL and Caltech under Principal Investigator James Bock, selected under NASA's MIDEX program at a cost of roughly $500 million. Its three science objectives: probing cosmic inflation via the large-scale distribution of hundreds of millions of galaxies (primordial non-Gaussianity, f_NL); tracing galaxy evolution via intensity mapping of the cosmic web; and surveying protostellar clouds and planet-forming disks for water ice and other pre-biotic molecules within the Milky Way."),
  h2("3.2 Instrument"),
  p("SPHEREx uses a 20 cm aperture three-mirror anastigmat design with an unusually wide field of view (3.5\u00d711 degrees, ~39.5 deg\u00b2 per exposure \u2014 about 180 times the area of the full Moon). Rather than dispersive optics, it uses Linear Variable Filters over two Teledyne H2RG HgCdTe detector arrays (0.75\u20132.44 \u03bcm and 2.40\u20135.01 \u03bcm), reconstructing a full 102-band spectrum per pixel from multiple offset exposures. Detectors are passively cooled to 55 K via nested sunshields, with ~10 microkelvin RMS thermal stability. SPHEREx surveys the full sky every six months (~600 spectroscopic images/day), completing four full-sky surveys over its 25-month prime mission."),
  h2("3.3 Orbit and Pointing Constraints"),
  p("SPHEREx flies a sun-synchronous polar orbit at 675 km, with strict pointing constraints: 90\u2013100 degrees from the Sun, and no more than 35 degrees from nadir, both primarily for passive thermal management. The 35-degree nadir constraint incidentally reduces exposure to the highest-density regions of satellite traffic near Earth's limb, but does not eliminate it \u2014 675 km sits squarely within the main Starlink and megaconstellation orbital shells."),
  h2("3.4 Comparison with Other LEO Telescopes"),
  table(
    ["Parameter", "SPHEREx", "Hubble", "Xuntian (China)", "ARRAKIHS (ESA)"],
    [
      ["Altitude (km)", "675", "~540", "~400\u2013450", "~700"],
      ["Field of view (deg\u00b2)", "39.5", "~0.01", "~1.4", "~0.7"],
      ["Wavelength coverage", "0.75\u20135.0 \u03bcm", "UV\u2013near-IR", "0.255\u20131.0 \u03bcm", "0.6\u20131.65 \u03bcm"],
      ["Status (2026)", "Active (Mar 2025)", "Active (1990)", "Planned ~2026", "Planned 2030s"],
    ], [2400, 1750, 1750, 1900, 1550]),
  p("(Source: Borlaff et al. 2025, Nature, Table ED2.)"),

  h1("4. How Satellites Contaminate a Space Telescope"),
  h2("4.1 Trails in Optical and Infrared"),
  p("A satellite crossing a telescope's field of view during an exposure leaves a straight streak on the detector. At optical wavelengths, brightness depends on reflected sunlight \u2014 satellite size, reflectivity, and Sun-satellite-telescope geometry. At infrared wavelengths, where SPHEREx operates, thermal self-emission becomes a second, independent contribution: any satellite warmed by the Sun radiates most strongly in the mid-infrared but still contributes meaningfully in SPHEREx's 2.4\u20135.0 \u03bcm band. Because satellites give off both reflected light and heat, blocking them out completely in the infrared is effectively impossible \u2014 darkening a surface reduces reflection but cannot reduce a satellite's temperature to absolute zero."),
  h2("4.2 The Solar-Panel Problem"),
  p("SpaceX has oriented Starlink satellites edge-on to the ground to reduce reflected brightness for ground-based observers. This inadvertently worsens the infrared picture for space telescopes: with the satellite body edge-on to Earth, its solar panels \u2014 still Sun-facing \u2014 present their full illuminated, warm face to any telescope in LEO pointing away from the Sun, exactly as SPHEREx does by design."),
  h2("4.3 Field-of-View Exposure"),
  p("Contamination probability scales roughly with exposure area. SPHEREx's 39.5 deg\u00b2 field is about 4,000 times larger than Hubble's main camera. Its higher altitude and strict pointing constraints partially offset this, giving SPHEREx a contamination profile worse than Hubble but better than Xuntian or ARRAKIHS in absolute trail count, while sharing a near-identical fraction of affected exposures (>96% at full constellation build-out, per Borlaff et al. 2025) because even a single trail in such a large frame counts as contamination."),
  h2("4.4 Surface Brightness"),
  p("Surface brightness (mag/arcsec\u00b2, lower = brighter) quantifies how a trail compares to the faint sky backgrounds SPHEREx is designed to measure. Borlaff et al. (2025) report SPHEREx trails average ~19 \u00b1 2 mag/arcsec\u00b2 \u2014 substantially brighter than the science signal, and wide enough (several arcminutes) that the affected region, once local-background recalibration is included, exceeds the trail's own width."),

  h1("5. Original Analysis: Reflectance-Based Brightness Modelling"),
  p("The following is the original undergraduate-level photometric analysis (2025\u201326): a first-principles reflectance model for four representative satellite types, evaluated as a function of range. It does not include orbital propagation, thermal-IR modelling, or population statistics \u2014 those are addressed from scratch in the extension beginning at \u00a76."),
  table(
    ["Satellite", "Diameter D (m)", "Albedo p", "Angular velocity \u03c9 (arcsec/s)"],
    [
      ["Starlink V1.0", "6.50", "0.250", "237.37"],
      ["Starlink V1.5", "5.30", "0.250", "241.94"],
      ["Starlink V2 Mini", "11.50", "0.055", "246.00"],
      ["OneWeb (Gen 1)", "3.91", "0.250", "243.00"],
    ], [3350, 2000, 2000, 2000]),
  img(R + "extracted_imgs/p18_img0.png", 460, 246),
  caption("Figure 5.1. Reflectance-based surface brightness vs. range for four satellite types (original analysis)."),
  p("Surface brightness decreases roughly as the square of distance for all four satellites, most steeply within the first few hundred kilometres. At short range even the smallest satellite (OneWeb Gen 1) produces a trail bright enough to seriously contaminate an exposure; by 2,000 km all four have faded substantially, though remain measurable."),
  img(R + "extracted_imgs/p20_img0.png", 460, 246),
  caption("Figure 5.2. Population-averaged surface brightness vs. range, with min\u2013max band across all modelled satellite types (original analysis)."),
  p("The black curve is the range-dependent mean surface brightness across the full modelled population (not just the four satellites plotted individually); the shaded band gives the brightest-to-faintest spread at each range. This average \u2014 rather than any single satellite's curve \u2014 is the physically relevant quantity for mission-level contamination assessment, since SPHEREx has no way to know in advance which satellite type will cross its field of view. This analysis notes, but does not model, that SPHEREx's own thermal self-emission contribution would further raise these brightness estimates at the reddest wavelengths \u2014 the gap addressed directly in \u00a77.4 below."),

  new Paragraph({ children: [new PageBreak()] }),
  h1("6. Extended Methodology: Real-Orbital-Data Validation"),
  p("Sections 6\u20139 report a from-scratch extension, built independently of \u00a75, using real orbital data rather than an idealized four-satellite reflectance model. Every numeric result is either a direct output of a script run for this work or is explicitly marked as an external, cited value."),
  h2("6.1 Real orbital data"),
  p("All orbital elements are real, live two-line elements (TLEs) retrieved in September 2026 via Celestrak. SPHEREx: NORAD 63182, TLE epoch 19 Jul 2026. Six real Starlink satellites at ~53.15\u201353.16\u00b0 inclination (NORAD 48294, 48375, 48646, 47650, 47796, 44768; TLE epochs early August 2026), chosen to span a genuine spread of right ascension of ascending node (23.6\u00b0 to 266.4\u00b0). One real OneWeb satellite (NORAD 55158, ~1225 km, 87.9\u00b0 inclination; TLE epoch mid-September 2026). All propagation uses the sgp4 reference-implementation library in the TEME frame; because every derived quantity here is a difference between two state vectors expressed in the same frame, no further frame transformation is required."),
  h2("6.2 Boresight and field-of-view definition"),
  p("The boresight is fixed at the North Ecliptic Pole (RA 270\u00b0, Dec +66.56\u00b0) \u2014 a representative, illustrative pointing, not SPHEREx's literal real-time survey track, which sweeps the whole sky over each 6-month survey. A local tangent-plane frame built from the celestial RA/Dec basis vectors at the boresight is used to test a target's position against the FOV's 3.5\u00b0\u00d711\u00b0 half-widths. Earth occlusion is tested via the closest approach of the observer\u2013target line segment to Earth's centre."),
  h2("6.3 Monte Carlo statistical model (idealized shells)"),
  p("A statistical model treats each megaconstellation as circular-orbit shells (fixed altitude + inclination per operator/generation, from public design data), with satellite right ascension of ascending node and orbital phase drawn independently and uniformly at random. ~2.1 million synthetic configurations were sampled across 8 shells (Starlink V1.0/V1.5/V2-Mini, OneWeb, Amazon Leo, Guowang, Qianfan), checked against the FOV using \u00a76.2's geometry, with SPHEREx's own orbital phase independently randomized across one full real SGP4-propagated orbit."),
  h2("6.4 Direct real-catalog validation"),
  p("Independently of \u00a76.3's statistical assumptions, the six real Starlink satellites and the one real OneWeb satellite were propagated together with SPHEREx's real orbit over a genuine 30-day window at 10-second resolution, and every actual FOV-crossing event was counted directly \u2014 no random sampling, no independence assumption, no idealized substitution."),
  h2("6.5 Blackbody thermal-IR photometry"),
  p("For each real crossing event, a radiative-equilibrium temperature is estimated from a simple energy balance (absorbed solar flux at 1 AU = re-radiated thermal flux; albedo from the same values used in \u00a75). Planck's law is evaluated across 102 log-spaced bands spanning SPHEREx's two detectors (51 over 0.75\u20132.44 \u03bcm, 51 over 2.40\u20135.01 \u03bcm). A reflected-sunlight spectrum is computed identically, treating the Sun as a 5778 K blackbody attenuated by distance and albedo."),
  h2("6.6 TLE positional-uncertainty error budget"),
  p("SGP4/TLE accuracy is well characterised in the literature as ~1 km at epoch, degrading by a further 1\u20133 km/day (consistent across multiple independent sources). This work adopts 1 km + 2 km/day (midpoint) as a 1-sigma isotropic position uncertainty scaled by each object's actual age, and Monte Carlo perturbs both objects' positions 20,000 times per real crossing event (36 events total) to propagate this into range, phase-angle, and brightness uncertainty."),

  new Paragraph({ children: [new PageBreak()] }),
  h1("7. Extended Results"),
  h2("7.1 Full-exposure-window propagation (illustrative single-pair case)"),
  p("SPHEREx and real satellite OneWeb-0617 were propagated together across a single 112.5-second exposure window (0.5 s resolution) at a representative epoch (16 Sept 2026, 06:00 UTC):"),
  table(
    ["Quantity", "Value"],
    [
      ["SPHEREx altitude (this epoch)", "648.5 km"],
      ["OneWeb-0617 altitude", "1214.3 km"],
      ["Range, exposure start \u2192 end (+112.5s)", "12,770 \u2192 13,161 km"],
      ["Phase angle from boresight", "59.7\u00b0 \u2013 65.7\u00b0"],
      ["Apparent angular velocity", "195.7 \u2013 207.1 arcsec/s"],
      ["FOV encounter this pair/epoch?", "No \u2014 off-frame"],
    ], [4400, 4950]),
  img(R + "figs/fig1_angular_velocity.png", 440, 290),
  caption("Figure 7.1. Apparent angular velocity of OneWeb-0617 as seen from SPHEREx, from real SGP4 state vectors across the full exposure window."),
  p("This single pair did not cross the FOV at this epoch \u2014 individual conjunctions are rare per exposure, which is exactly why the population approach in \u00a77.2 is needed."),

  h2("7.2 Contamination rate for today's real satellite population"),
  table(
    ["Population component", "Satellites modelled", "Trails/exposure", "Basis"],
    [
      ["Starlink V1.0 + V1.5", "~7,000", "1.823", "Real-catalog (30-day direct SGP4 propagation)"],
      ["Starlink V2-Mini", "~2,357", "0.346", "Idealized shell"],
      ["OneWeb", "652", "0.072", "Idealized shell (1 real sat.: 0/30 days, consistent but not independent confirmation)"],
      ["Amazon Leo + Guowang + Qianfan", "331", "0.032", "Idealized shell"],
      ["Total (current, ~10,340 tracked)", "10,340", "~2.27", "Blended"],
    ], [2900, 1600, 1500, 3350]),
  img(R + "figs/fig4_trail_rate_breakdown.png", 440, 300),
  caption("Figure 7.2. Current-population trail-rate breakdown. Green = validated by direct propagation of real orbits; amber = idealized statistical shell, not independently checked."),
  p("The real-catalog check came out higher than the idealized model for the Starlink shell (0.911 vs 0.303 trails/exposure, from 36 real crossing events over 30 real days across 6 real satellites) \u2014 ruling out \u201creal orbital-plane phasing suppresses the rate\u201d as an explanation for anything found in \u00a77.3."),

  h2("7.3 Full build-out projection \u2014 an open discrepancy"),
  p("Extrapolating \u00a76.3's idealized model to Borlaff et al.'s 560,000-satellite scenario (published result: 5.6 \u00b1 0.3 trails/exposure for SPHEREx) gives 64.9 \u2014 roughly 11\u00d7 higher. Three candidate explanations were tested directly:"),
  bullet("Eclipse filtering \u2014 verified correct (33% eclipse fraction on an unconstrained sample) but 100% of FOV-crossing satellites were already sunlit; a real selection effect, not the cause."),
  bullet("Photometric detection threshold \u2014 real crossing events (14\u201320 mag/arcsec\u00b2) were comfortably brighter than Borlaff's stated 22.3 mag/arcsec\u00b2 threshold; not the cause."),
  bullet("Boresight-declination coincidence \u2014 averaging over 60 random sky pointings gave 95.2, higher than the fixed-boresight result, not lower; ruled out."),
  p("The leading untested hypothesis is that a real 560,000-satellite population would spread across far more distinct orbital planes and altitude bands than the representative shell set used here \u2014 a factor that would require per-operator FCC/ITU filing data this work does not have access to. No independently-derived full-build-out number is presented; Borlaff et al.'s (2025) published 5.6 \u00b1 0.3 is cited directly wherever the future scenario is discussed."),

  h2("7.4 Thermal-infrared vs. reflected-light photometry"),
  p("Estimated radiative-equilibrium satellite temperature: 316 K (S=1361 W/m\u00b2, albedo 0.25, IR emissivity 0.9, two-sided radiating panel). Because both thermal and reflected flux scale identically with (satellite radius/range)\u00b2, their ratio depends only on wavelength and the two blackbody temperatures (316 K vs. the Sun's 5778 K) \u2014 confirmed across all 36 real crossing events without exception."),
  img(R + "figs/fig3_blackbody_spectrum.png", 460, 320),
  caption("Figure 7.3. Thermal (316 K) vs. reflected-sunlight flux across SPHEREx's 102 bands, representative real crossing event. Thermal dominates beyond ~3.76 \u03bcm \u2014 SPHEREx's long-wavelength detector sits almost entirely in the thermally-dominated regime."),
  p("This quantifies, for the first time in this project, exactly where \u00a75's original qualitative observation becomes true: below ~3.76 \u03bcm reflected sunlight dominates; above it, thermal emission does \u2014 meaning essentially all of SPHEREx's long-wavelength detector operates in a regime \u00a75's brightness-vs-distance model did not include."),

  h2("7.5 TLE positional-uncertainty error budget"),
  img(R + "figs/fig5_tle_uncertainty.png", 420, 300),
  caption("Figure 7.4. Range uncertainty (1-sigma, Monte Carlo, N=20,000/event) for each of 36 real crossing events, vs. range."),
  table(
    ["Quantity", "Value"],
    [
      ["Median relative range uncertainty (36 events)", "3.16%"],
      ["Range of relative uncertainty across events", "1.32% \u2013 32.69%"],
      ["Median resulting photometric uncertainty", "\u00b10.069 mag"],
      ["Input (cited, not assumed)", "1 km epoch + 2 km/day growth, both objects"],
    ], [5400, 3950]),

  h1("8. Limitations"),
  bullet("Boresight fixed at the North Ecliptic Pole throughout \u2014 representative, not a true survey-averaged pointing; \u00a77.3's random-pointing test suggests other sky positions could differ by roughly 2\u20132.5\u00d7."),
  bullet("The full build-out (560,000-satellite) projection is not independently validated (\u00a77.3); Borlaff et al.'s published figure is used directly for any future-scenario statement."),
  bullet("Idealized-shell estimates for Starlink V2-Mini, OneWeb, Amazon Leo, Guowang, and Qianfan are not real-catalog-checked to the same standard as Starlink V1.0/V1.5; only one real OneWeb satellite was checked, with an inconclusive (though not contradictory) zero-crossing result."),
  bullet("Satellite physical parameters (diameter, albedo) are the same representative values used in \u00a75, not manufacturer specifications for each individual real satellite propagated."),
  bullet("The radiative-equilibrium temperature model (\u00a76.5) is a simple energy-balance estimate; it does not model satellite attitude, eclipse thermal cycling, or material-specific emissivity."),

  h1("9. Conclusions"),
  p("Satellite megaconstellations in Low Earth Orbit directly contaminate space telescope images from within the same orbital band these instruments occupy, making avoidance essentially impossible by design. Simple mitigations such as surface darkening do not address the infrared regime SPHEREx observes in, since thermal emission depends on temperature, not reflectivity \u2014 a claim this work now quantifies directly: thermal emission overtakes reflected sunlight above ~3.76 \u03bcm, meaning SPHEREx's entire long-wavelength detector operates in a regime the original reflectance-only model (\u00a75) did not capture."),
  p("At today's real satellite population, this work's from-scratch, real-orbital-data extension estimates ~2.3 trail-crossing events per exposure at a representative sky pointing, with the dominant contribution independently confirmed by direct propagation of real, currently-orbiting satellites rather than a statistical model alone \u2014 to our knowledge the first time this specific validation step has been carried out for this project. The extension to a full 560,000-satellite future scenario remains an open discrepancy with the published literature (\u00a77.3): investigated directly, not resolved, and reported as such."),
  p("Next steps: extend real-catalog validation to OneWeb, Kuiper, Guowang, and Qianfan with a larger real-satellite sample; obtain or approximate real multi-shell orbital-plane distributions for future-scenario testing; average the encounter-rate calculation over a realistic SPHEREx survey-pointing sequence; and begin drafting a submission-ready manuscript from \u00a76 onward."),

  h1("References"),
  p("Borlaff, A. S., Marcum, P., & Howell, S. (2025). Satellite megaconstellations will threaten space-based astronomy. Nature. https://doi.org/10.1038/s41586-025-09759-5", { size: 20 }),
  p("Crill, B. P., et al. (2020). SPHEREx: NASA's near-infrared spectrophotometric all-sky survey. Proceedings of SPIE 11443.", { size: 20 }),
  p("Gong, Y., et al. (2019). Cosmology from the Chinese Space Station Optical Survey (CSS-OS). The Astrophysical Journal, 883, 203.", { size: 20 }),
  p("Corral van Damme, C., et al. (2024). ARRAKIHS: ESA's new fast-implementation science mission. Proceedings of SPIE 13092.", { size: 20 }),
  p("Celestrak (T.S. Kelso). NORAD two-line element sets, retrieved September 2026. https://celestrak.org", { size: 20 }),
  p("python-sgp4 library documentation \u2014 cited SGP4/TLE accuracy (~1 km at epoch, 1\u20133 km/day growth).", { size: 20 }),
];

const doc = new Document({ sections: [{ properties: { page: { size: { width: 12240, height: 15840 } } } }, ].map(s => ({ ...s, children })) });

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(R + "SPHEREx_combined_manuscript.docx", buf);
  console.log("Written.");
});
