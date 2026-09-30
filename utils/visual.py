"""
Minimal screenshot comparison helper (Playwright for Python has no built-in
``to_have_screenshot``).
"""

import io
from dataclasses import dataclass

import allure
from PIL import Image, ImageChops


@dataclass(frozen=True)
class ImageDiff:
    diff_ratio: float
    diff_image: bytes


def compare_screenshots(expected: bytes, actual: bytes, pixel_threshold: int = 16) -> ImageDiff:
    """Return the share of pixels that differ and a highlighted diff image.

    Args:
        expected: PNG bytes of the reference screenshot.
        actual: PNG bytes of the screenshot under test.
        pixel_threshold: Per-channel difference (0-255) ignored as anti-aliasing noise.
    """
    expected_img = Image.open(io.BytesIO(expected)).convert("RGB")
    actual_img = Image.open(io.BytesIO(actual)).convert("RGB")
    if expected_img.size != actual_img.size:
        width = max(expected_img.width, actual_img.width)
        height = max(expected_img.height, actual_img.height)
        expected_img = _pad(expected_img, width, height)
        actual_img = _pad(actual_img, width, height)

    mask = (
        ImageChops.difference(expected_img, actual_img)
        .convert("L")
        .point(lambda value: 255 if value > pixel_threshold else 0)
    )
    changed = mask.histogram()[255]
    ratio = changed / (mask.width * mask.height)

    highlighted = actual_img.copy()
    highlighted.paste((255, 0, 255), mask=mask)
    buffer = io.BytesIO()
    highlighted.save(buffer, format="PNG")
    return ImageDiff(diff_ratio=ratio, diff_image=buffer.getvalue())


def attach_comparison(expected: bytes, actual: bytes, diff: ImageDiff) -> None:
    allure.attach(expected, "expected", allure.attachment_type.PNG)
    allure.attach(actual, "actual", allure.attachment_type.PNG)
    allure.attach(diff.diff_image, f"diff ({diff.diff_ratio:.2%} of pixels)", allure.attachment_type.PNG)


def _pad(image: Image.Image, width: int, height: int) -> Image.Image:
    canvas = Image.new("RGB", (width, height), (0, 0, 0))
    canvas.paste(image, (0, 0))
    return canvas
