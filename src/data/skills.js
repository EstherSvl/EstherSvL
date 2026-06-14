// The Glass Artist's Grid — skill data
//
// Layout note: x/y are coordinates on a ~1600x1300 canvas. The grid radiates
// outward from a central "Foundations" cluster, FFX-sphere-grid style, with
// each discipline forming an arm. Cross-links between arms create the loops
// that make the grid feel like a connected web rather than a simple tree.

export const DISCIPLINES = {
  foundations: { id: 'foundations', label: 'Foundations', color: '#E0A526', glow: '#ffd968' },
  stained:     { id: 'stained',     label: 'Stained Glass', color: '#2F6BB0', glow: '#6fa8e6' },
  painting:    { id: 'painting',    label: 'Painting & Surface', color: '#B23A4C', glow: '#e87b8a' },
  kiln:        { id: 'kiln',        label: 'Kiln Glass', color: '#2E9B6B', glow: '#65d6a3' },
  hot:         { id: 'hot',         label: 'Hot Glass', color: '#D7732B', glow: '#ffac6b' },
  engraving:   { id: 'engraving',   label: 'Engraving & Texture', color: '#7E57B5', glow: '#b48fe6' },
}

// State order used when cycling a node by clicking it.
export const STATES = ['locked', 'learning', 'practiced', 'mastered']

export const STATE_META = {
  locked:    { label: 'Not started', short: 'Locked' },
  learning:  { label: 'Learning',    short: 'Learning' },
  practiced: { label: 'Practiced',   short: 'Practiced' },
  mastered:  { label: 'Mastered',    short: 'Mastered' },
}

export const SKILLS = [
  // ---------- Foundations (centre hub) ----------
  {
    id: 'safety',
    name: 'Studio Safety & Setup',
    discipline: 'foundations',
    x: 800, y: 620, hub: true,
    prereqs: [],
    summary: 'The first node. Glass cuts, lead and kiln fumes, hot torches — set up a workspace that keeps you making for decades.',
    details: 'Lead hygiene (no eating at the bench, washing up), eye protection, ventilation for soldering and kiln firing, safe glass storage and disposal of offcuts, first-aid for cuts and burns. Everything else on this grid builds on a studio you can work in safely.',
  },
  {
    id: 'glass-cutting',
    name: 'Glass Cutting',
    discipline: 'foundations',
    x: 660, y: 520,
    prereqs: ['safety'],
    summary: 'Scoring and breaking glass to a line — the single most-used skill across every flat-glass discipline.',
    details: 'Using a cutter to make one clean score, then running the break with pliers, hands or a running tool. Straight cuts, inside and outside curves, circles, and reading how different glasses break. Grozing and basic grinding to refine an edge.',
  },
  {
    id: 'design-cartoon',
    name: 'Design & Cartooning',
    discipline: 'foundations',
    x: 940, y: 520,
    prereqs: ['safety'],
    summary: 'Turning an idea into a full-size working drawing (a "cartoon") with cut-lines, colours and numbered pieces.',
    details: 'Composition, scaling a design to size, drawing cut-lines that respect the strength of lead or foil, and making pattern templates. The blueprint that painting, leadwork and foil all follow.',
  },
  {
    id: 'colour-glass',
    name: 'Colour & Glass Selection',
    discipline: 'foundations',
    x: 800, y: 760,
    prereqs: ['safety'],
    summary: 'Knowing your materials: cathedral vs opalescent, COE for fusing, antique vs machine-rolled, and how light moves through colour.',
    details: 'Reading glass for colour, texture and transmission, understanding compatibility (coefficient of expansion) for anything that goes in a kiln, and choosing glass that suits the technique — leaded, fused or blown.',
  },

  // ---------- Stained Glass (upper-left arm) ----------
  {
    id: 'copper-foil',
    name: 'Copper Foil (Tiffany)',
    discipline: 'stained',
    x: 470, y: 470,
    prereqs: ['glass-cutting'],
    summary: 'The Tiffany method: wrapping each glass edge in copper foil so intricate, three-dimensional pieces can be soldered together.',
    details: 'Foiling tightly and burnishing, suited to small pieces, curves and lampshades where lead came is too bulky. The route to Tiffany-style shades and boxes.',
  },
  {
    id: 'leadwork',
    name: 'Leadworking (Came)',
    discipline: 'stained',
    x: 560, y: 380,
    prereqs: ['glass-cutting'],
    summary: 'Stretching, cutting and shaping lead came — the H-section channel that holds glass in traditional windows.',
    details: 'Stretching came to harden it, cutting clean joints, fitting glass into the channels, and building up a panel on a board against battens. The structural craft behind leaded windows.',
  },
  {
    id: 'soldering',
    name: 'Soldering',
    discipline: 'stained',
    x: 420, y: 360,
    prereqs: ['copper-foil'],
    summary: 'Joining foil seams or lead came joints with molten solder — smooth beads for Tiffany, neat joints for leaded panels.',
    details: 'Flux, heat control, and a steady run for a rounded bead on copper-foil seams; flat tinned joints on lead came. The skill that turns loose pieces into one rigid panel.',
  },
  {
    id: 'glass-in-lead',
    name: 'Glass in Lead (Panels)',
    discipline: 'stained',
    x: 360, y: 280,
    prereqs: ['leadwork', 'soldering'],
    summary: 'Building a complete leaded panel: glass set in came, soldered, then cemented and polished into a weatherproof whole.',
    details: 'Cementing (puttying) under the came flanges for strength and weatherproofing, cleaning, and finishing. A full traditional stained-glass panel from cartoon to finished work.',
  },
  {
    id: 'bevels',
    name: 'Bevels & Jewels',
    discipline: 'stained',
    x: 320, y: 560,
    prereqs: ['glass-cutting'],
    summary: 'Working with bevelled glass and pressed jewels that catch and refract light in a panel.',
    details: 'Incorporating ready-made bevels, nuggets and jewels, and the basics of grinding your own bevel facets for prismatic highlights in clear and coloured work.',
  },
  {
    id: 'installation',
    name: 'Installing Windows',
    discipline: 'stained',
    x: 230, y: 200,
    prereqs: ['glass-in-lead'],
    summary: 'Fitting finished panels into actual window openings — measuring, reinforcing, weatherproofing and safe installation.',
    details: 'Surveying an opening, building to size, adding tie-bars and reinforcement, fitting into frames, sealing against weather, and (for large works) plating and protective glazing. Where the panel becomes part of a building.',
  },

  // ---------- Painting & Surface (upper-right arm) ----------
  {
    id: 'glass-painting',
    name: 'Glass Painting',
    discipline: 'painting',
    x: 1040, y: 460,
    prereqs: ['design-cartoon'],
    summary: 'Painting with vitreous (glass) paint that is kiln-fired permanently into the surface — trace lines and matt shading.',
    details: 'Mixing and applying vitreous paint, laying tracing lines for detail and matting/shading for tone and modelling, then firing to fuse the paint to the glass. The traditional language of figurative stained glass.',
  },
  {
    id: 'hard-edge',
    name: 'Hard-Edge Line Work',
    discipline: 'painting',
    x: 1190, y: 400,
    prereqs: ['glass-painting'],
    summary: 'Crisp, confident trace lines — the controlled "hard edge" that defines features and drawing in painted glass.',
    details: 'Brush control for clean, unbroken lines of varying weight, stick-lighting (working over a light source), and reinforcing or stopping out so lines survive firing sharp and dark.',
  },
  {
    id: 'silver-stain',
    name: 'Silver / Yellow Stain',
    discipline: 'painting',
    x: 1190, y: 540,
    prereqs: ['glass-painting'],
    summary: 'Silver-nitrate stain fired onto the back of glass to produce transparent yellows and ambers — the original "stain" in stained glass.',
    details: 'Applying silver stain for ranges from pale lemon to deep amber, controlling strength by firing, and using it for hair, halos, borders and detail without adding a separate piece of glass.',
  },
  {
    id: 'kiln-firing',
    name: 'Kiln Firing (Paint)',
    discipline: 'painting',
    x: 1330, y: 460,
    prereqs: ['glass-painting'],
    summary: 'Reading and running a kiln for painted and stained work — schedules, temperatures and avoiding ruined firings.',
    details: 'Firing ranges for paint, stain and enamel, kiln-wash and setup, ramp/soak schedules, and recognising under- and over-firing. Shared backbone for everything that goes through heat.',
  },
  {
    id: 'enamels',
    name: 'Glass Enamels',
    discipline: 'painting',
    x: 1470, y: 480,
    prereqs: ['kiln-firing', 'silver-stain'],
    summary: 'Coloured low-fire enamels for painterly, full-colour imagery fired onto a single sheet of glass.',
    details: 'Layering transparent and opaque enamels, multiple firings, and combining with trace and stain for painted panels in the manner of later painted glass.',
  },
  {
    id: 'gilding',
    name: 'Gilding',
    discipline: 'painting',
    x: 1300, y: 590,
    prereqs: ['glass-painting'],
    summary: 'Applying gold (and other metal) leaf to glass — including verre églomisé, gilding on the reverse for mirror-bright detail.',
    details: 'Laying loose leaf onto size or water-gilding behind glass, burnishing, backing up and engraving into the leaf for ornament, lettering and luminous highlights.',
  },

  // ---------- Kiln Glass (lower-left arm) ----------
  {
    id: 'fusing',
    name: 'Fusing',
    discipline: 'kiln',
    x: 640, y: 800,
    prereqs: ['colour-glass'],
    summary: 'Heating compatible glass until pieces fuse together — tack-fused texture through to a fully flat, glossy sheet.',
    details: 'Stacking compatible (matched-COE) glass, tack and full-fuse schedules, controlling bubbles, and combining sheet, frit and stringer into new sheets and panels.',
  },
  {
    id: 'mold-making',
    name: 'Mould Making',
    discipline: 'kiln',
    x: 540, y: 900,
    prereqs: ['fusing'],
    summary: 'Making and using moulds — slumping formers and refractory casting moulds that shape glass in the kiln.',
    details: 'Ready-made and hand-built slumping moulds, plus investment/refractory moulds taken from an original for casting. Kiln-wash, venting and release so glass shapes cleanly and lets go.',
  },
  {
    id: 'slumping',
    name: 'Slumping',
    discipline: 'kiln',
    x: 440, y: 810,
    prereqs: ['fusing', 'mold-making'],
    summary: 'Letting a fused sheet soften and drape over or into a mould to make bowls, dishes and dimensional forms.',
    details: 'Lower-temperature schedules that bend rather than fully melt glass, controlling the slump for even walls, and combining fusing then slumping in staged firings.',
  },
  {
    id: 'kiln-casting',
    name: 'Kiln Casting / Pâte de Verre',
    discipline: 'kiln',
    x: 380, y: 920,
    prereqs: ['mold-making', 'fusing'],
    summary: 'Filling a refractory mould with glass and melting it to cast solid, sculptural forms — including delicate pâte de verre.',
    details: 'Lost-wax and open-face casting, packing frit for pâte de verre, long annealing for thick work, and devesting and cold-finishing the casting. The sculptural end of kiln glass.',
  },

  // ---------- Hot Glass (lower arm) ----------
  {
    id: 'lampworking',
    name: 'Lampworking (Flamework)',
    discipline: 'hot',
    x: 760, y: 920,
    prereqs: ['safety'],
    summary: 'Shaping glass rod and tube at a torch flame — beads, pendants, figurines and scientific-style forms.',
    details: 'Flame control, gathering and shaping molten rod on a mandrel or in air, marvering and tooling, and managing thermal shock with a flame-annealing or batch-annealing routine.',
  },
  {
    id: 'glassblowing',
    name: 'Glassblowing',
    discipline: 'hot',
    x: 910, y: 940,
    prereqs: ['safety', 'colour-glass'],
    summary: 'Gathering molten glass on a blowpipe from a furnace and inflating, shaping and colouring it — vessels and sculpture.',
    details: 'Gathering, marvering, blowing and shaping with jacks and blocks, applying colour, transferring to a punty, and opening forms. A team, furnace-based hot-shop discipline.',
  },
  {
    id: 'murrine',
    name: 'Murrine & Cane',
    discipline: 'hot',
    x: 680, y: 1030,
    prereqs: ['lampworking'],
    summary: 'Pulling patterned cane and slicing murrine — the cross-section "pictures in glass" used in beads, blowing and fusing.',
    details: 'Building up coloured cane, pulling it down to scale, and cutting murrine slices to arrange into patterns. Crosses over into both fusing and blown work.',
  },
  {
    id: 'annealing',
    name: 'Annealing & Heat Control',
    discipline: 'hot',
    x: 830, y: 1050,
    prereqs: ['glassblowing'],
    summary: 'Cooling hot glass slowly through its stress range so finished work does not crack — the make-or-break of hot glass.',
    details: 'Understanding the annealing range, soak times scaled to thickness, and reading and avoiding internal stress. The discipline that decides whether hot work survives the night.',
  },

  // ---------- Engraving & Texture (right arm, the cross-roads) ----------
  {
    id: 'cold-working',
    name: 'Cold Working',
    discipline: 'engraving',
    x: 1000, y: 800,
    prereqs: ['glass-cutting'],
    summary: 'Grinding, cutting, smoothing and polishing cold glass — the finishing skill that links kiln, hot and engraved work.',
    details: 'Flat-bed grinding, lap wheels, diamond pads, linishing and polishing to refine edges and surfaces, level fused pieces, and finish castings and blown work. A hub that touches every cold-finishing job.',
  },
  {
    id: 'metal-engraving',
    name: 'Metal Engraving',
    discipline: 'engraving',
    x: 1080, y: 680,
    prereqs: ['design-cartoon'],
    summary: 'Hand-engraving metal with a graver — a transferable cutting and line discipline that feeds directly into glass engraving and gilding ornament.',
    details: 'Sharpening and controlling a graver, cutting clean lines and lettering in copper, brass or silver, and the eye for ornament that carries over to engraving glass and decorating leaf.',
  },
  {
    id: 'engraving-etching',
    name: 'Glass Engraving & Etching',
    discipline: 'engraving',
    x: 1240, y: 690,
    prereqs: ['metal-engraving', 'cold-working'],
    summary: 'Cutting decoration into the glass surface — drill/point and wheel engraving, plus acid and cream etching for frosted designs.',
    details: 'Diamond-point and rotary-burr engraving, copper-wheel engraving for depth, and acid/cream etching through a resist for matt and tonal effects. Surface drawing that is part of the glass itself.',
  },
  {
    id: 'sandblasting',
    name: 'Sandblasting',
    discipline: 'engraving',
    x: 1140, y: 820,
    prereqs: ['design-cartoon'],
    summary: 'Blasting abrasive through a stencil to frost, shade or carve depth into the glass surface.',
    details: 'Cutting and applying resist masks, surface frosting, graded/tonal blasting, and deeper stage-carving for relief. Pairs naturally with cold working and etching for surface design.',
  },
]

// Cross-links that aren't strict prerequisites but show how arms connect,
// giving the grid its FFX-style loops. Drawn as faint paths.
export const CROSS_LINKS = [
  ['fusing', 'cold-working'],
  ['glassblowing', 'cold-working'],
  ['kiln-casting', 'cold-working'],
  ['sandblasting', 'cold-working'],
  ['engraving-etching', 'gilding'],
  ['murrine', 'fusing'],
  ['colour-glass', 'fusing'],
  ['bevels', 'cold-working'],
]
