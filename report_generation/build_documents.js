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
const R = require("path").join(__dirname, "..") + "/";
const EXT_H = { h1, h2, p, bullet, caption, img, table, R };

const EXT = require('./ext_content.js')(EXT_H);
const children = [
  new Paragraph({ children: [new TextRun({ text: "Investigation of Celestial Events and Megaconstellation Effects on Space Telescopes", bold: true, size: 32 })], alignment: AlignmentType.CENTER, spacing: { after: 120 } }),
  new Paragraph({ children: [new TextRun({ text: "A Case Study of NASA's SPHEREx, with an Extended Real-Orbital-Data Analysis", italics: true, size: 24 })], alignment: AlignmentType.CENTER, spacing: { after: 300 } }),
  new Paragraph({ children: [new TextRun({ text: "Joshanraj C V", size: 22 })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
  new Paragraph({ children: [new TextRun({ text: "B.Sc. Physics, SRM Institute of Science and Technology (SRM KTR), Chennai", size: 20 })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
  new Paragraph({ children: [new TextRun({ text: "Original undergraduate project supervised by Dr. Tushar H. Rana, Department of Physics and Nanotechnology (submitted April 2026); extended analysis conducted independently thereafter", size: 18, italics: true })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
  new Paragraph({ children: [new TextRun({ text: "Status: manuscript in preparation, not yet submitted for publication", size: 20, italics: true })], alignment: AlignmentType.CENTER, spacing: { after: 300 } }),

  h1("Abstract"),
  p("Satellite megaconstellations in Low Earth Orbit increasingly share the altitudes used by space telescopes. NASA's SPHEREx \u2014 a wide-field (39.5 deg\u00b2), 102-band near-infrared all-sky survey launched in March 2025 into a ~650 km Sun-synchronous orbit \u2014 is a natural test case. This work has two parts. The first is an original reflectance-based photometric model (undergraduate project, 2025\u201326) of trail surface brightness versus range for four representative satellite types. The second is a from-scratch computational extension built on real orbital data: SGP4 propagation of real satellites, a Monte Carlo encounter model that applies SPHEREx's actual survey constraints (35\u00b0 maximum zenith angle, 91\u00b0 solar avoidance, 112.5 s exposures), a one-year real-orbit validation, blackbody thermal-infrared photometry across SPHEREx's 102 bands, and a TLE positional-uncertainty error budget."),
  p("The central physical result is geometric: under SPHEREx's 35\u00b0 zenith limit, every line of sight climbs away from Earth, so only satellites orbiting above ~650 km can ever cross the field. All Starlink and Amazon Leo shells contribute exactly zero (0 crossings in ~3.2 million simulated valid exposures). Summing the publicly filed constellations above SPHEREx's orbit (OneWeb, Guowang GW-2, Qianfan, Telesat Lightspeed; ~28,500 satellites) predicts 4.5 \u00b1 0.2 trails per exposure at full build-out, versus 5.64 (+0.28/\u22120.27) published by Borlaff et al. (2025). The residual corresponds to ~7,500 additional high-altitude satellites in that study's registry, and lies inside this model's real-orbit validation band (3.7\u20137.4). At today's population the rate is ~0.13 trails per exposure (about one exposure in eight), carried entirely by OneWeb and early Qianfan. Observable crossings are near-overhead (median range 635 km), sweep the field at ~1.2\u00b0/s, and above ~3.76 \u03bcm are dominated by the satellite's own thermal emission rather than reflected sunlight. An earlier version of this analysis reported ~2.3 trails per exposure; that figure came from a pointing SPHEREx never uses and is withdrawn (\u00a77.2)."),

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
      ["China (state)", "Guowang", "~29", "12,992", "~590 (GW-A59); ~1,145 (GW-2)"],
      ["SSST (China)", "Qianfan", "~108", "~15,000", "~1,160"],
    ], [2400, 2400, 1750, 1750, 1050]),
  p("Starlink alone held roughly 75% of all active satellites as of December 2025. Amazon's Project Kuiper (rebranded Amazon Leo in November 2025) is ramping production at up to five satellites per day. China's Guowang (state-owned) and Qianfan (commercial) together represent a comparable future Chinese LEO infrastructure."),
  h2("2.3 Growth Trajectory"),
  p("Active LEO satellite counts grew from roughly 400 in 2000, to 2,000 at Starlink's first launch (2019), to about 15,000 by 2025 \u2014 and industry filings project roughly 100,000 by 2030 and up to 560,000 at full constellation build-out by the late 2030s. That 560,000 figure is not a worst-case hypothetical; it is what has actually been filed with regulators."),
  h2("2.4 Orbital Overlap with Astronomy"),
  p("Almost all megaconstellation satellites operate between 340 and 1,200 km altitude \u2014 precisely the band most LEO space telescopes occupy. SPHEREx orbits at ~650 km; Hubble at ~540 km; China's planned Xuntian telescope at 400\u2013450 km. This overlap is not accidental: Low Earth Orbit is where internet satellites need to be for competitive signal latency (a 550 km satellite has under 30 ms round-trip delay, versus ~600 ms from geostationary orbit)."),
  p("Any LEO satellite, warmed by the Sun, radiates thermally in the infrared \u2014 a mechanism reflective-surface darkening (used to mitigate optical brightness for ground-based astronomers) does essentially nothing to address, since thermal emission is a function of temperature, not surface colour."),

  h1("3. The SPHEREx Mission"),
  h2("3.1 Overview and Science Goals"),
  p("SPHEREx (Spectro-Photometer for the History of the Universe, Epoch of Reionization, and Ices Explorer) launched 11 March 2025 on a Falcon 9 from Vandenberg Space Force Base, managed by JPL and Caltech under Principal Investigator James Bock, selected under NASA's MIDEX program at a cost of roughly $500 million. Its three science objectives: probing cosmic inflation via the large-scale distribution of hundreds of millions of galaxies (primordial non-Gaussianity, f_NL); tracing galaxy evolution via intensity mapping of the cosmic web; and surveying protostellar clouds and planet-forming disks for water ice and other pre-biotic molecules within the Milky Way."),
  h2("3.2 Instrument"),
  p("SPHEREx uses a 20 cm aperture three-mirror anastigmat design with an unusually wide field of view (3.5\u00d711 degrees, ~39.5 deg\u00b2 per exposure \u2014 about 180 times the area of the full Moon). Rather than dispersive optics, it uses Linear Variable Filters over two Teledyne H2RG HgCdTe detector arrays (0.75\u20132.44 \u03bcm and 2.40\u20135.01 \u03bcm), reconstructing a full 102-band spectrum per pixel from multiple offset exposures. Detectors are passively cooled to 55 K via nested sunshields, with ~10 microkelvin RMS thermal stability. SPHEREx surveys the full sky every six months (~600 spectroscopic images/day), completing four full-sky surveys over its 25-month prime mission."),
  h2("3.3 Orbit and Pointing Constraints"),
  p("SPHEREx flies a terminator-aligned Sun-synchronous orbit at ~650 km. Its survey pointings are restricted to within 35\u00b0 of local zenith (i.e. looking away from Earth, never toward the limb) and to at least 91\u00b0 from the Sun throughout each 112.5 s exposure, both primarily for thermal management (Borlaff et al. 2025, Methods). These two rules turn out to control SPHEREx's exposure to satellites almost completely: \u00a77.3 shows that the zenith limit alone makes every satellite orbiting below SPHEREx geometrically invisible to it."),
  h2("3.4 Comparison with Other LEO Telescopes"),
  table(
    ["Parameter", "SPHEREx", "Hubble", "Xuntian (China)", "ARRAKIHS (ESA)"],
    [
      ["Altitude (km)", "~650", "~540", "~400\u2013450", "~700"],
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
  p("Contamination probability scales roughly with exposure area. SPHEREx's 39.5 deg\u00b2 field is about 4,000 times larger than Hubble's main camera. Its higher altitude and strict pointing constraints partially offset this, giving SPHEREx a contamination profile worse than Hubble but better than Xuntian or ARRAKIHS in absolute trail count, while sharing a near-identical fraction of affected exposures (more than 92% of SPHEREx exposures at full build-out, per Borlaff et al. 2025) because even a single trail in such a large frame counts as contamination."),
  h2("4.4 Surface Brightness"),
  p("Surface brightness (mag/arcsec\u00b2, lower = brighter) quantifies how a trail compares to the faint sky backgrounds SPHEREx is designed to measure. Borlaff et al. (2025) report a median SPHEREx trail surface brightness of 21.1 (+1.9/\u22123.0) mag/arcsec\u00b2 \u2014 substantially brighter than the science signal, and wide enough (several arcminutes) that the affected region, once local-background recalibration is included, exceeds the trail's own width."),

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
  img(R + "figures/original_fig5.1_brightness_vs_distance.png", 460, 246),
  caption("Figure 5.1. Reflectance-based surface brightness vs. range for four satellite types (original analysis)."),
  p("Surface brightness decreases roughly as the square of distance for all four satellites, most steeply within the first few hundred kilometres. At short range even the smallest satellite (OneWeb Gen 1) produces a trail bright enough to seriously contaminate an exposure; by 2,000 km all four have faded substantially, though remain measurable."),
  img(R + "figures/original_fig5.2_brightness_vs_distance_average.png", 460, 246),
  caption("Figure 5.2. Population-averaged surface brightness vs. range, with min\u2013max band across all modelled satellite types (original analysis)."),
  p("The black curve is the range-dependent mean surface brightness across the full modelled population (not just the four satellites plotted individually); the shaded band gives the brightest-to-faintest spread at each range. This average \u2014 rather than any single satellite's curve \u2014 is the physically relevant quantity for mission-level contamination assessment, since SPHEREx has no way to know in advance which satellite type will cross its field of view. This analysis notes, but does not model, that SPHEREx's own thermal self-emission contribution would further raise these brightness estimates at the reddest wavelengths \u2014 the gap addressed directly in \u00a77.4 below."),

  new Paragraph({ children: [new PageBreak()] }),
  ...EXT,
  h1("References"),
  p("Borlaff, A. S., Marcum, P., & Howell, S. (2025). Satellite megaconstellations will threaten space-based astronomy. Nature. https://doi.org/10.1038/s41586-025-09759-5", { size: 20 }),
  p("Crill, B. P., et al. (2020). SPHEREx: NASA's near-infrared spectrophotometric all-sky survey. Proceedings of SPIE 11443.", { size: 20 }),
  p("Gong, Y., et al. (2019). Cosmology from the Chinese Space Station Optical Survey (CSS-OS). The Astrophysical Journal, 883, 203.", { size: 20 }),
  p("Corral van Damme, C., et al. (2024). ARRAKIHS: ESA's new fast-implementation science mission. Proceedings of SPIE 13092.", { size: 20 }),
  p("Celestrak (T.S. Kelso). NORAD two-line element sets, retrieved September 2026. https://celestrak.org", { size: 20 }),
  p("python-sgp4 library documentation \u2014 cited SGP4/TLE accuracy (~1 km at epoch, 1\u20133 km/day growth).", { size: 20 }),
  p("Borlaff, A. S., Marcum, P., & Howell, S. (2026). Author Correction: Satellite megaconstellations will threaten space-based astronomy. Nature 654, E14. https://doi.org/10.1038/s41586-026-10553-0 (corrects ARRAKIHS values only; SPHEREx values unchanged).", { size: 20 }),
  p("Guowang constellation shells (GW-2 ~1,145 km; GW-A59 ~590 km) and Qianfan planned altitude (~1,160 km): CircleID, \u201cChinese LEO Satellite Internet Update: Guowang, Qianfan, and Honghu-3\u201d; Wikipedia, \u201cGuowang\u201d (accessed September 2026).", { size: 20 }),
];

const doc = new Document({ sections: [{ properties: { page: { size: { width: 12240, height: 15840 } } }, children }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(R + "SPHEREx_combined_manuscript.docx", buf); console.log("combined written"); });

// ---- standalone extension report: title + scope note + revision note + sections 6-9 + references
const reportChildren = [
  new Paragraph({ children: [new TextRun({ text: "Satellite Megaconstellation Contamination of NASA's SPHEREx", bold: true, size: 32 })], alignment: AlignmentType.CENTER, spacing: { after: 120 } }),
  new Paragraph({ children: [new TextRun({ text: "Extension report: real-orbital-data analysis (revised September 2026)", italics: true, size: 24 })], alignment: AlignmentType.CENTER, spacing: { after: 300 } }),
  new Paragraph({ children: [new TextRun({ text: "Joshanraj C V", size: 22 })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
  new Paragraph({ children: [new TextRun({ text: "B.Sc. Physics, SRM Institute of Science and Technology (SRM KTR), Chennai", size: 20 })], alignment: AlignmentType.CENTER, spacing: { after: 300 } }),
  h2("A note on scope"),
  p("This report is separate from the undergraduate thesis \u201cInvestigation on Celestial Events and Megaconstellation Effects on Telescopes\u201d (SRM Institute of Science and Technology, April 2026, supervised by Dr. Tushar H. Rana), which used a reflectivity-based surface-brightness model for four representative satellites and did not include orbital propagation, Monte Carlo statistics, blackbody modelling or TLE error analysis. Everything below was computed afterwards, from real orbital data. Section numbers follow the combined manuscript."),
  h2("What changed in this revision"),
  bullet("SPHEREx's real survey constraints (35\u00b0 maximum zenith angle, 91\u00b0 solar avoidance) are now applied, with random accessible pointings in place of a fixed North Ecliptic Pole boresight."),
  bullet("Guowang and Qianfan altitudes corrected to their filed values (~1,145 km and ~1,160 km); no proportional scaling to 560,000 satellites."),
  bullet("Time step converged (0.1 s); the previous 7.5\u201310 s steps missed fast near-overhead crossings."),
  bullet("Full-build-out prediction revised from 64.9 to 4.5 \u00b1 0.2 trails/exposure (Borlaff et al.: 5.64). The earlier ~2.3 trails/exposure current-population figure is withdrawn; the corrected value is ~0.13."),
  bullet("Per-event photometry and the TLE error budget are recomputed on 962 physically observable crossings instead of 36 fixed-NEP events."),
  new Paragraph({ children: [new PageBreak()] }),
  ...EXT,
  h1("References"),
  ...children.slice(children.length - 8),
];
const doc2 = new Document({ sections: [{ properties: { page: { size: { width: 12240, height: 15840 } } }, children: reportChildren }] });
Packer.toBuffer(doc2).then(buf => { fs.writeFileSync(R + "SPHEREx_extension_report.docx", buf); console.log("report written"); });
