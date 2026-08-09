"""End-to-end jobs, checked the way you would check a print.

``tools/make_gallery.py`` composes a spread of realistic pairings and lays them
out to be looked at. These are the same jobs with the judgements a person makes
in front of that contact sheet written down: is there ink, is it inside the
object, and did the background actually come off.

Every assertion here started as something visible in the picture and invisible
in the old tests, which used flat shapes on flat white and stayed green through
all of it:

* a motif exported with margins around it landed at seventy per cent of the
  size it was asked for, off-centre by however lopsided the padding was;
* a repeat whose motifs touch the edge of the tile had its background reading
  inverted — the tool removed the flowers and kept the paper, and on a white
  plate that is invisible until you print it on green glass;
* a graded studio backdrop came along with the subject, because the ground was
  measured against a single colour;
* a pale subject on pale ground came out full of holes and halos at every
  tolerance, with nothing said about it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import gallery_art as art  # noqa: E402
import make_gallery  # noqa: E402

from glassprint import masks, segment  # noqa: E402
from glassprint.compose import ComposeSpec, compose  # noqa: E402
from glassprint.pattern import Placement  # noqa: E402
from glassprint.raster import Raster  # noqa: E402

JOBS = {job.name: job for job in make_gallery.jobs()}


@pytest.fixture(scope="module")
def ran() -> dict:
    """Every job, composed once and shared — the whole set takes a few seconds."""
    return {name: make_gallery.run(job)[1] for name, job in JOBS.items()}


# --- what has to be true of every job ---------------------------------------


@pytest.mark.parametrize("name", sorted(JOBS))
def test_ink_lands_on_the_object_and_nowhere_else(name, ran):
    """Clipping is on for all of these, so print off the edge is a scrap."""
    assert ran[name]["spill"] < 0.005, f"{name} prints outside the target shape"


@pytest.mark.parametrize("name", sorted(JOBS))
def test_something_actually_prints(name, ran):
    """A job that lays down nothing is a failure that writes a file happily."""
    assert ran[name]["filled"] > 0.02, f"{name} covers almost none of the shape"


@pytest.mark.parametrize("name", sorted(JOBS))
def test_a_background_that_was_removed_stays_removed(name, ran):
    """The whole shape solid with ink means the cut-out kept the paper.

    This is the one that hid. On a near-white plate a kept white ground looks
    exactly like a working result; it only shows up as a slab when you print it
    onto coloured glass, by which point you have used the glass.
    """
    if "remove" not in (JOBS[name].spec.keep or "") and not JOBS[name].spec.layers:
        pytest.skip("no background instruction in this job")
    assert ran[name]["filled"] < 0.90, f"{name} covers the whole shape — background kept?"


# --- the specific things that were broken -----------------------------------


def _content_box(rgba: np.ndarray) -> tuple[int, int, int, int]:
    return masks.bbox(rgba[:, :, 3].astype(np.float32) / 255.0, threshold=0.35)


def _padded(raster: Raster, factor: float = 2.2) -> Raster:
    """The same artwork on a much bigger canvas, off to one side."""
    height = int(raster.height * factor)
    width = int(raster.width * factor)
    canvas = np.zeros((height, width, 4), dtype=np.uint8)
    canvas[10 : 10 + raster.height, 10 : 10 + raster.width] = raster.rgba
    return Raster(canvas, dpi=raster.dpi)


def test_padding_around_a_motif_does_not_shrink_it():
    """A flower on a big canvas must land the same size as one on a tight canvas.

    Procreate hands you whatever canvas you drew on. Scaling that to the target
    scales the empty space with it, and the artwork arrives small — which is
    what "it worked very poorly" looks like from the outside.
    """
    base = art.base_coaster()
    tight = art.overlay_gold_leaf()
    spec = ComposeSpec(placement=Placement(fit="contain", scale=0.9))

    snug = compose(base, tight, spec).overlay_layer.rgba
    roomy = compose(base, _padded(tight), spec).overlay_layer.rgba

    a, b = _content_box(snug), _content_box(roomy)
    snug_w, roomy_w = a[2] - a[0], b[2] - b[0]
    assert abs(snug_w - roomy_w) / snug_w < 0.06, (
        f"padding changed the printed size: {snug_w}px vs {roomy_w}px"
    )


def test_padding_does_not_push_a_motif_off_centre():
    base = art.base_coaster()
    tight = art.overlay_gold_leaf()
    spec = ComposeSpec(placement=Placement(fit="contain", scale=0.8))

    for overlay in (tight, _padded(tight)):
        box = _content_box(compose(base, overlay, spec).overlay_layer.rgba)
        centre_x = (box[0] + box[2]) / 2 / base.width
        centre_y = (box[1] + box[3]) / 2 / base.height
        assert abs(centre_x - 0.5) < 0.04, f"off-centre horizontally: {centre_x:.3f}"
        assert abs(centre_y - 0.5) < 0.04, f"off-centre vertically: {centre_y:.3f}"


def test_a_repeat_whose_motifs_touch_the_edge_is_not_read_inside_out():
    """The border of a tile is not a sample of its background.

    A repeat *is* motifs running off the canvas edge, so the border can easily
    be more flower than paper. Taking the median of it made the reference red,
    and the tool then removed the flowers and kept the ground, confidently.
    """
    tile = art.overlay_seamless_floral()
    background = segment.background_mask(tile, tolerance=1.0)
    assert background.mean() > 0.55, (
        f"only {background.mean():.0%} read as background — the ground is most of this tile"
    )


def test_a_graded_backdrop_is_still_a_backdrop():
    """A studio sweep falls off toward the corners; one colour cannot describe it."""
    photo = art.overlay_orchid_on_gradient()
    background = segment.background_mask(photo, tolerance=1.0)
    assert background.mean() > 0.6, (
        f"only {background.mean():.0%} of a graded backdrop was recognised"
    )


def test_a_pale_subject_on_pale_ground_is_flagged_rather_than_guessed_at():
    """White orchids on white paper: no tolerance separates them, so say so.

    Measured across the whole range, the flowers and the shadow they cast move
    together — the best the colour heuristic ever manages is two fifths of the
    flower and a fifth of the paper. Tuning the number gives a different bad
    answer, not a good one, so the tool has to name the situation.
    """
    backends = segment.Backends()
    segment.background_mask(art.overlay_orchid_on_white(), 1.0, backends=backends)
    assert any("barely a different colour" in note for note in backends.notes), backends.notes


def test_artwork_that_separates_cleanly_is_not_nagged_about():
    """The warning is worth nothing if it fires on work that came out right."""
    for name in ("seamless-floral", "scattered-motifs", "orchid-on-gradient"):
        backends = segment.Backends()
        segment.background_mask(art.OVERLAYS[name](), 1.0, backends=backends)
        assert not any("barely a different" in note for note in backends.notes), name


def test_a_lens_cutout_is_never_printed_over():
    """A hole in the alpha is a hole in the object, not an area to fill.

    Filling holes is right for a ragged silhouette and wrong here: ink over the
    camera is a scrapped case, and it costs the case to find out.
    """
    case = art.base_phone_case()
    result = compose(
        case, art.overlay_orchid_cutout(),
        ComposeSpec(placement=Placement(fit="contain", scale=0.95)),
    )
    lens = (case.alpha_f < 0.5) & _inside_top(case)
    ink = result.overlay_layer.rgba[:, :, 3].astype(np.float32) / 255.0
    assert float(ink[lens].max()) < 0.02, "printed over the lens cutout"


def _inside_top(raster: Raster) -> np.ndarray:
    """The upper region where the cutout lives, excluding the outer margin."""
    keep = np.zeros((raster.height, raster.width), dtype=bool)
    top, bottom = int(raster.height * 0.04), int(raster.height * 0.28)
    left, right = int(raster.width * 0.08), int(raster.width * 0.55)
    keep[top:bottom, left:right] = True
    return keep


def test_a_pattern_stays_inside_a_silhouette_that_is_not_its_bounding_box():
    """A vase is a fifth as wide at the neck as at the belly."""
    result = compose(
        art.base_vase(), art.overlay_seamless_floral(),
        ComposeSpec(
            keep="remove the white background",
            placement=Placement(fit="tile", repeat_across=4),
        ),
    )
    shape = result.shape_mask
    ink = result.overlay_layer.rgba[:, :, 3].astype(np.float32) / 255.0
    outside = float((ink * (1.0 - shape)).sum()) / max(float(ink.sum()), 1e-6)
    assert outside < 0.005, f"{outside:.1%} of the ink is off the vase"


# --- printing the pattern and not the field ---------------------------------


def test_texture_finds_markings_that_brightness_cannot():
    """The case: veins on a petal, with a blown-out background in the same frame.

    Both are pale, so a brightness threshold takes both and lays a solid slab of
    ink over the part of the glass you most wanted to see through. A vein is not
    "light", it is lighter *than the petal around it* — which stays true in the
    shadowed half of the flower, where the threshold has given up anyway.
    """
    photo = art.overlay_veined_orchid()
    bright = segment.resolve(segment.Selector("tone", "light"), photo)
    veins = segment.texture_mask(photo)

    # The background is the outer eighth of the frame; the bloom is nowhere near it.
    edge = np.zeros(bright.shape, dtype=bool)
    edge[: bright.shape[0] // 8, :] = edge[-bright.shape[0] // 8 :, :] = True
    edge[:, : bright.shape[1] // 8] = edge[:, -bright.shape[1] // 8 :] = True

    # Judged at the threshold the printer actually lays ink at, because that is
    # what ends up on the glass. Below it nothing is printed either way.
    slab = float((bright[edge] > 0.5).mean())
    specks = float((veins[edge] > 0.5).mean())

    assert slab > 0.05, "fixture no longer has a bright background to be fooled by"
    assert specks < slab / 20, (
        f"brightness put ink on {slab:.1%} of the background, texture on {specks:.2%}"
    )
    assert specks < 0.002, f"{specks:.2%} of the background would still print as specks"
    assert float((veins > 0.5).mean()) > 0.01, "texture selection found no markings at all"


def test_texture_reads_markings_either_way_up():
    """Veins on a petal are pale; ink on paper is not. Same request, reversed."""
    photo = art.overlay_veined_orchid()
    assert segment.texture_mask(photo, polarity="light").mean() > 0
    # Line art is dark-on-light, and 'auto' has to notice that by itself.
    drawing = art.overlay_linework()
    auto = segment.texture_mask(drawing)
    dark = segment.texture_mask(drawing, polarity="dark")
    assert np.allclose(auto, dark), "auto picked the wrong polarity for line art"


def test_transparency_does_not_read_as_a_marking():
    """Empty canvas is absent, not black; left as zeros it rings like an edge."""
    sprig = art.overlay_gold_leaf()  # motif on transparency
    veins = segment.texture_mask(sprig)
    assert float(veins[sprig.alpha_f < 0.5].max()) < 0.01, "found markings in empty space"


def test_asking_for_the_veins_in_words_reaches_the_texture_selector():
    from glassprint import nl

    assert nl.parse("keep the veins").ops[0].selector.kind == "texture"
    assert nl.parse("just the pale veining").ops[0].selector.value == "light"
    assert nl.parse("keep the dark grain").ops[0].selector.value == "dark"
    # The words already spoken for must not be stolen.
    assert nl.parse("remove the white background").ops[0].selector.kind == "background"


def test_the_vein_print_puts_ink_on_almost_none_of_the_glass():
    """The whole point: the glass supplies the colour, the ink supplies the pattern.

    If this ever creeps up toward covering the panel, the tool has gone back to
    printing the field — which is the one outcome that wastes the coloured glass.
    """
    from glassprint.fade import Fade
    from glassprint.recolor import ColorSpec

    result = compose(
        art.base_coaster(), art.overlay_veined_orchid(),
        ComposeSpec(
            keep="keep the veins",
            placement=Placement(fit="contain", scale=0.9),
            color=ColorSpec(mode="tint", color="#ffffff", strength=1.0),
            fade=Fade(mode="linear", min_alpha=1.0, max_alpha=1.0, cutoff=0.5),
        ),
    )
    ink = result.overlay_layer.rgba[:, :, 3].astype(np.float32) / 255.0
    shape = result.shape_mask
    covered = float((ink > 0.5).sum()) / float((shape > 0.5).sum())
    assert 0.01 < covered < 0.15, f"veins cover {covered:.1%} of the panel"

    # And a cutoff means what is previewed is what lays down: nothing survives
    # in the band that the printer would silently drop.
    faint = ((ink > 0.02) & (ink < 0.5)).sum()
    assert faint == 0, f"{faint} pixels of ink sit below the print cliff"


# --- a cut layout, not a single object --------------------------------------


def _cut_sheet() -> Raster:
    """Three flowers' worth of glass parts nested for the printer bed.

    Two shades of one hue, because a layered piece is routinely built that way;
    white parts drawn as outlines on a white page, because that is what a cut
    file looks like; and green parts that must be left alone.
    """
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (900, 600), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    for x in (120, 380, 640):
        draw.ellipse((x, 60, x + 150, 210), fill=(185, 205, 245, 255), outline=(40, 40, 40, 255))
        draw.ellipse((x + 40, 250, x + 110, 320), fill=(58, 128, 190, 255), outline=(40, 40, 40, 255))
        draw.ellipse((x, 360, x + 150, 470), fill=(255, 255, 255, 255), outline=(40, 40, 40, 255))
        draw.ellipse((x + 20, 500, x + 130, 570), fill=(94, 205, 62, 255), outline=(40, 40, 40, 255))
    return Raster(np.array(image, dtype=np.uint8), dpi=(300.0, 300.0))


def test_two_shades_of_one_colour_are_told_apart():
    """"Light blue" and "dark blue" are not absolute brightnesses.

    On a layered piece both blues are pale — 0.80 and 0.45 luminance — so a band
    running to 0.38 calls neither of them dark, and the darker glass selects as
    nothing at all. The words mean the lighter and the darker of whatever shades
    are actually here.
    """
    from glassprint import nl

    sheet = _cut_sheet()
    light = segment.evaluate(nl.build_plan("the light blue shapes", sheet), sheet)
    dark = segment.evaluate(nl.build_plan("the dark blue shapes", sheet), sheet)

    assert light.mean() > 0.01 and dark.mean() > 0.001
    assert not np.allclose(light, dark), "the two shades came back identical"
    # Each names three pieces, one per flower, and they do not overlap.
    assert masks.component_count(masks.despeckle(light, 0.0004)) == 3
    assert masks.component_count(masks.despeckle(dark, 0.0004)) == 3
    assert float(masks.intersect(light, dark).mean()) < 0.001


def test_a_generic_noun_is_not_an_object_to_go_hunting_for():
    """"Shapes" and "pieces" name nothing; they used to force a model lookup."""
    from glassprint import nl

    for phrase in ("the light blue shapes", "the dark blue pieces", "the green glass"):
        assert nl.parse(phrase).ops[0].selector.kind == "color", phrase


def test_one_shade_present_selects_all_of_it_and_says_so():
    """Nothing to choose between is a fact worth stating, not a half to guess."""
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (300, 300), (255, 255, 255, 255))
    ImageDraw.Draw(image).ellipse((60, 60, 240, 240), fill=(58, 128, 190, 255))
    one_shade = Raster(np.array(image, dtype=np.uint8), dpi=(300.0, 300.0))

    backends = segment.Backends()
    found = segment.resolve(
        segment.Selector("color", "blue", tone="dark"), one_shade, backends
    )
    assert found.mean() > 0.1
    assert any("only one shade" in note.lower() for note in backends.notes), backends.notes


def test_each_piece_of_a_cut_layout_gets_the_whole_pattern():
    """A sheet of parts is not one object.

    The pieces are neighbours on the printer bed and nowhere near each other in
    the finished piece, so one pattern spanning the sheet gives each of them an
    arbitrary slice — which looks like artwork until you assemble it.
    """
    sheet = _cut_sheet()
    art = art_module.overlay_veined_orchid()
    spec = ComposeSpec(
        keep="keep the veins",
        target="describe", target_describe="the light blue shapes",
        placement=Placement(fit="cover"),
    )

    spanning = compose(sheet, art, spec)
    per_piece = compose(
        sheet, art,
        ComposeSpec(**{**spec.__dict__, "placement": Placement(fit="cover", per_piece=True)}),
    )

    assert any("separately on each" in note for note in per_piece.notes), per_piece.notes

    # Each piece should carry a comparable amount of pattern. Spanning one
    # pattern across three pieces cannot manage that.
    def spread(result):
        ink = result.overlay_layer.rgba[:, :, 3].astype(np.float32) / 255.0
        shares = [
            float((ink * piece).sum()) / max(float(piece.sum()), 1.0)
            for piece in masks.components(result.shape_mask, threshold=0.35)
        ]
        return max(shares) / max(min(shares), 1e-6)

    assert spread(per_piece) < spread(spanning), (
        "per-piece placement did not even out the pattern across the pieces"
    )


art_module = art


# --- laying artwork along the shape it goes on ------------------------------


def _leaf(angle_deg: float, size: int = 500) -> Raster:
    """A leaf silhouette at a chosen angle: broad at the base, pointed at the tip."""
    from PIL import Image, ImageDraw

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    blade = Image.new("RGBA", (int(size * 0.8), int(size * 0.34)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(blade)
    draw.polygon(
        [(0, blade.height // 2), (blade.width * 0.35, 0),
         (blade.width, blade.height * 0.45), (blade.width * 0.30, blade.height)],
        fill=(40, 130, 40, 255),
    )
    blade = blade.rotate(-angle_deg, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(
        blade, ((size - blade.width) // 2, (size - blade.height) // 2)
    )
    return Raster(np.array(canvas, dtype=np.uint8), dpi=(300.0, 300.0))


def test_the_long_axis_of_a_shape_is_found():
    """A leaf's midrib is its long axis, and that needs no model to locate."""
    for angle in (0, 30, 75, 120):
        found = masks.principal_axis(_leaf(angle).alpha_f)
        assert found is not None
        measured, _, elongation = found
        assert elongation > 1.2, f"a leaf should read as elongated, got {elongation:.2f}"
        # The axis is recovered modulo the 180° a bare axis cannot resolve.
        off = min((measured - angle) % 180.0, (angle - measured) % 180.0)
        assert off < 12.0, f"axis off by {off:.0f}° at {angle}°"


def test_a_round_shape_has_no_axis_to_align_to():
    """A circle's "long axis" is noise, and acting on it would be worse than not."""
    from PIL import Image, ImageDraw

    canvas = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    ImageDraw.Draw(canvas).ellipse((80, 80, 320, 320), fill=(40, 130, 40, 255))
    disc = Raster(np.array(canvas, dtype=np.uint8), dpi=(300.0, 300.0))

    _, _, elongation = masks.principal_axis(disc.alpha_f)
    assert elongation < masks.MIN_ELONGATION if hasattr(masks, "MIN_ELONGATION") else True

    result = compose(
        disc, _leaf(40),
        ComposeSpec(placement=Placement(fit="contain", align="shape")),
    )
    assert any("too round" in note for note in result.notes), result.notes


def test_artwork_is_turned_to_lie_along_the_target():
    """The three things asked for at once — rotate to match, size to it, line the
    middles up — are one operation, because the midrib is the long axis."""
    base = _leaf(115)
    art = _leaf(20)

    aligned = compose(base, art, ComposeSpec(placement=Placement(fit="contain", align="shape")))
    assert any("Turned the artwork" in note for note in aligned.notes), aligned.notes

    # The placed artwork should now share the base's axis, which it did not before.
    def axis_of(result):
        return masks.principal_axis(
            result.overlay_layer.rgba[:, :, 3].astype(np.float32) / 255.0
        )[0]

    target = masks.principal_axis(base.alpha_f)[0]
    plain = compose(base, art, ComposeSpec(placement=Placement(fit="contain")))

    def gap(measured):
        return min((measured - target) % 180.0, (target - measured) % 180.0)

    assert gap(axis_of(aligned)) < gap(axis_of(plain)), "alignment did not improve the angle"
    assert gap(axis_of(aligned)) < 12.0


def test_asking_in_words_reaches_the_alignment():
    from glassprint import talk

    for phrase in (
        "rotate the overlay to match the base leaf",
        "align it with the shape",
        "line the veins up with the leaf",
    ):
        assert talk.get_path(talk.respond(phrase, {}).spec, "placement.align") == "shape", phrase
    assert talk.get_path(talk.respond("tile it four across", {}).spec, "placement.align") is None
