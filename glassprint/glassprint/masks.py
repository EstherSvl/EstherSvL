"""Soft-mask helpers.

A mask is a float32 array in 0..1 with the same height and width as the image
it belongs to. Soft edges matter for print: a hard 1-bit cutout shows stair-step
artefacts on curves, which a UV printer reproduces faithfully.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


def zeros(shape: tuple[int, int]) -> np.ndarray:
    return np.zeros(shape, dtype=np.float32)


def ones(shape: tuple[int, int]) -> np.ndarray:
    return np.ones(shape, dtype=np.float32)


def clean(mask: np.ndarray) -> np.ndarray:
    return np.clip(np.nan_to_num(mask.astype(np.float32), nan=0.0), 0.0, 1.0)


def union(*masks: np.ndarray) -> np.ndarray:
    out = clean(masks[0])
    for m in masks[1:]:
        out = np.maximum(out, clean(m))
    return out


def intersect(*masks: np.ndarray) -> np.ndarray:
    out = clean(masks[0])
    for m in masks[1:]:
        out = out * clean(m)
    return out


def subtract(mask: np.ndarray, other: np.ndarray) -> np.ndarray:
    return clean(clean(mask) * (1.0 - clean(other)))


def invert(mask: np.ndarray) -> np.ndarray:
    return 1.0 - clean(mask)


def feather(mask: np.ndarray, radius: float) -> np.ndarray:
    """Gaussian-soften the mask edge by ``radius`` pixels."""
    if radius <= 0:
        return clean(mask)
    img = Image.fromarray((clean(mask) * 255).astype(np.uint8), mode="L")
    img = img.filter(ImageFilter.GaussianBlur(radius=float(radius)))
    return np.asarray(img, dtype=np.float32) / 255.0


def grow(mask: np.ndarray, pixels: float) -> np.ndarray:
    """Spread (positive) or choke (negative) the mask by ``pixels``."""
    pixels = float(pixels)
    if abs(pixels) < 0.5:
        return clean(mask)
    size = int(abs(round(pixels))) * 2 + 1
    data = clean(mask)
    if pixels > 0:
        return clean(ndimage.grey_dilation(data, size=(size, size)))
    return clean(ndimage.grey_erosion(data, size=(size, size)))


def binarize(mask: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    return (clean(mask) >= threshold).astype(bool)


def fill_holes(mask: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    filled = ndimage.binary_fill_holes(binarize(mask, threshold))
    return union(mask, filled.astype(np.float32))


def despeckle(mask: np.ndarray, min_area_fraction: float = 0.0008, threshold: float = 0.5) -> np.ndarray:
    """Drop connected blobs smaller than ``min_area_fraction`` of the image."""
    binary = binarize(mask, threshold)
    if not binary.any():
        return clean(mask)
    labels, count = ndimage.label(binary)
    if count == 0:
        return clean(mask)
    min_area = max(1, int(min_area_fraction * binary.size))
    sizes = ndimage.sum(binary, labels, index=np.arange(1, count + 1))
    keep = np.concatenate([[False], sizes >= min_area])
    return clean(mask) * keep[labels].astype(np.float32)


def largest_component(mask: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    binary = binarize(mask, threshold)
    if not binary.any():
        return clean(mask)
    labels, count = ndimage.label(binary)
    if count <= 1:
        return clean(mask)
    sizes = ndimage.sum(binary, labels, index=np.arange(1, count + 1))
    winner = int(np.argmax(sizes)) + 1
    return clean(mask) * (labels == winner).astype(np.float32)


def principal_axis(mask: np.ndarray) -> tuple[float, tuple[float, float], float] | None:
    """The long axis of a shape: its angle, its centre, and how elongated it is.

    A leaf's midrib *is* its long axis, and so is the spine of a petal or the
    run of a vase. That is what makes this useful for registration: to lay the
    veins of a photographed leaf onto a drawn leaf you do not need to find the
    midrib in either picture, you need the axis of each silhouette, which is an
    ordinary second-moment calculation and needs no model.

    The angle is in degrees, measured clockwise from horizontal in image
    coordinates (y downward). Elongation is the ratio of the long axis to the
    short one: 1.0 is a circle, where the angle means nothing at all.
    """
    ys, xs = np.nonzero(mask > 0.5)
    if ys.size < 16:
        return None

    weights = mask[ys, xs].astype(np.float64)
    total = weights.sum()
    if total <= 0:
        return None

    cx = float((xs * weights).sum() / total)
    cy = float((ys * weights).sum() / total)
    x, y = xs - cx, ys - cy

    xx = float((weights * x * x).sum() / total)
    yy = float((weights * y * y).sum() / total)
    xy = float((weights * x * y).sum() / total)

    angle = 0.5 * math.atan2(2.0 * xy, xx - yy)
    # Eigenvalues of the covariance, for how much of an axis this really is.
    spread = math.sqrt(max((xx - yy) ** 2 + 4.0 * xy * xy, 0.0))
    major, minor = (xx + yy + spread) / 2.0, (xx + yy - spread) / 2.0
    elongation = math.sqrt(major / minor) if minor > 1e-9 else float("inf")

    # An axis has no direction, so a leaf could come out end for end. Which end
    # is which is settled by where the mass sits: a leaf, a petal and a teardrop
    # are all broad at one end and pointed at the other.
    along = x * math.cos(angle) + y * math.sin(angle)
    skew = float((weights * along**3).sum() / total)
    if skew > 0:
        angle += math.pi

    return math.degrees(angle) % 360.0, (cx, cy), elongation


def components(
    mask: np.ndarray, threshold: float = 0.5, min_area_fraction: float = 0.0002
) -> list[np.ndarray]:
    """Each separate region of the mask, on its own, largest first.

    For artwork that goes onto one object this is never needed. For a cut
    layout — a sheet of glass pieces to be printed and then assembled — it is
    the whole thing: each piece wants its own copy of the pattern, sized and
    centred on itself, not a fragment of one pattern spanning the sheet.
    """
    binary = binarize(mask, threshold)
    if not binary.any():
        return []
    labels, count = ndimage.label(binary)
    if count <= 1:
        return [clean(mask)]

    floor = min_area_fraction * mask.size
    sizes = ndimage.sum(binary, labels, index=np.arange(1, count + 1))
    order = np.argsort(sizes)[::-1]
    found = [
        clean(mask) * (labels == int(index) + 1).astype(np.float32)
        for index in order
        if sizes[index] >= floor
    ]
    return found or [clean(mask)]


def component_count(mask: np.ndarray, threshold: float = 0.5) -> int:
    binary = binarize(mask, threshold)
    if not binary.any():
        return 0
    _, count = ndimage.label(binary)
    return int(count)


def coverage(mask: np.ndarray) -> float:
    return float(clean(mask).mean())


def bbox(mask: np.ndarray, threshold: float = 0.5) -> tuple[int, int, int, int] | None:
    """Bounding box of the mask as ``(left, top, right, bottom)``, exclusive."""
    binary = binarize(mask, threshold)
    if not binary.any():
        return None
    rows = np.flatnonzero(binary.any(axis=1))
    cols = np.flatnonzero(binary.any(axis=0))
    return int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1


def touching_border(mask: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Keep only components that touch the image border."""
    binary = binarize(mask, threshold)
    if not binary.any():
        return clean(mask)
    labels, count = ndimage.label(binary)
    if count == 0:
        return clean(mask)
    edge_labels = set(labels[0, :].tolist()) | set(labels[-1, :].tolist())
    edge_labels |= set(labels[:, 0].tolist()) | set(labels[:, -1].tolist())
    edge_labels.discard(0)
    if not edge_labels:
        return zeros(mask.shape)
    keep = np.isin(labels, list(edge_labels))
    return clean(mask) * keep.astype(np.float32)


def resize(mask: np.ndarray, width: int, height: int) -> np.ndarray:
    if mask.shape == (height, width):
        return clean(mask)
    img = Image.fromarray((clean(mask) * 255).astype(np.uint8), mode="L")
    img = img.resize((max(1, width), max(1, height)), Image.BILINEAR)
    return np.asarray(img, dtype=np.float32) / 255.0
