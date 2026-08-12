"""Getting a file ready for a printer that cannot print half a drop.

Art software fades things by making them transparent. A UV printer cannot do
that: at each spot it either fires a drop or it does not, and below about half
coverage the dither has so little to work with that nothing lands at all. So a
soft airbrushed falloff — the most ordinary thing in the world to draw — is
reproduced as solid ink that stops dead partway along.

Worse with a white underbase, because the underbase is generated *from the same
alpha*. The white ramps too, and the white and the colour do not cross the cliff
at exactly the same place, so there is a band where colour prints with little or
no white behind it. On clear or opal material that reads as a transparent tint
against an opaque pastel, which is the mottled edge you get instead of a fade.

The fix is not a setting. It is to stop asking for the impossible: carry the
gradient in the *colour* and keep every pixel of the piece fully opaque, so the
only transparency in the file is outside the cut line. Then the halftone carries
the tone, which is what a halftone is for.

:func:`preflight` measures how much of a file is in the dead band.
:func:`flatten` does the conversion.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .colors import parse_color
from .fade import ALPHA_CLIFF
from .raster import Raster


@dataclass
class Preflight:
    """What a file will lose on the way to the printer."""

    #: Fraction of the artwork (anything visible at all) that sits under the
    #: cliff and will therefore print as nothing.
    doomed: float
    #: Fraction sitting in the anxious band just above it, which will print but
    #: thinly and is where speckle lives.
    marginal: float
    #: Fraction at effectively full opacity — the part that is safe.
    solid: float
    #: How much of the canvas the artwork occupies at all.
    covered: float
    notes: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return self.doomed < 0.02

    def as_dict(self) -> dict:
        return {
            "doomed": round(self.doomed, 4),
            "marginal": round(self.marginal, 4),
            "solid": round(self.solid, 4),
            "covered": round(self.covered, 4),
            "clean": self.clean,
            "notes": self.notes,
        }


def preflight(raster: Raster, *, cliff: float = ALPHA_CLIFF) -> Preflight:
    """Measure the alpha, and say what the printer will do with it.

    Everything is a fraction of the *visible artwork*, not of the canvas —
    a motif on a big empty page would otherwise report as almost entirely fine
    no matter how badly it fades.
    """
    from scipy import ndimage

    alpha = raster.alpha_f
    visible = alpha > 0.004
    # Every edge in every image is anti-aliased, so there is always a rim of
    # part-transparent pixels a pixel or two wide. That rim is not a fade and
    # counting it would make every well-drawn file look broken, so the artwork
    # is eroded before anything is measured. What survives is the interior,
    # where a real gradient lives.
    interior = ndimage.binary_erosion(visible, iterations=2)
    if interior.any():
        visible = interior
    total = float(visible.sum())
    if total < 1:
        return Preflight(0.0, 0.0, 0.0, 0.0, ["Nothing visible in this file at all."])

    values = alpha[visible]
    doomed = float((values < cliff).sum()) / total
    marginal = float(((values >= cliff) & (values < 0.9)).sum()) / total
    solid = float((values >= 0.9).sum()) / total

    notes: list[str] = []
    if doomed > 0.25:
        notes.append(
            f"{doomed:.0%} of the artwork is under {cliff:.0%} alpha and will print as "
            "nothing — the fade will stop dead rather than fading. Carry it in the "
            "colour instead: flatten onto an opaque ground."
        )
    elif doomed > 0.02:
        notes.append(
            f"{doomed:.0%} of the artwork is under {cliff:.0%} alpha and will not print. "
            "Usually that is a soft edge, and it will come out harder than drawn."
        )
    if marginal > 0.25:
        notes.append(
            f"{marginal:.0%} sits between {cliff:.0%} and full. That prints, but thinly, "
            "and with a white underbase it is where speckle shows."
        )
    if not notes:
        notes.append("Alpha is safe: nothing meaningful sits under the print cliff.")
    return Preflight(doomed, marginal, solid, total / alpha.size, notes)


def flatten(
    raster: Raster,
    ground: str | tuple[int, int, int] = "#ffffff",
    *,
    edge: float = ALPHA_CLIFF,
    feather_edge: bool = True,
) -> Raster:
    """Move the gradient out of the alpha and into the colour.

    Everything the piece contains is composited onto ``ground`` and turned fully
    opaque; everything outside the cut line goes fully transparent. The picture
    is unchanged against that ground — but now there is no ramp for the printer
    to threshold, and the white underbase comes out as the piece's own shape,
    solid, instead of a fade with a cliff in it.

    ``edge`` is where the cut line falls. It defaults to the same place the
    printer gives up, so nothing that was going to print is thrown away and
    nothing that was not is kept.
    """
    rgb_ground = parse_color(ground) or (255, 255, 255)
    alpha = raster.alpha_f
    rgb = raster.rgb_f

    over = rgb * alpha[:, :, None] + (np.array(rgb_ground, np.float32) / 255.0) * (
        1.0 - alpha[:, :, None]
    )

    inside = (alpha >= edge).astype(np.float32)
    if feather_edge:
        # Softened by a fixed *pixel* radius, not by a window in alpha. On a
        # gentle airbrush a narrow alpha window is still dozens of pixels wide,
        # which would put the ramp — and the cliff — straight back in.
        from . import masks

        inside = masks.feather(inside, 0.7)

    out = np.dstack([
        np.clip(over * 255.0 + 0.5, 0, 255),
        np.clip(inside * 255.0 + 0.5, 0, 255),
    ]).astype(np.uint8)
    return Raster(out, dpi=raster.dpi, source_format=raster.source_format, name=raster.name)
