"""
RefExplain AI - Icon Generator
Generates clean PNG icons (16x16, 48x48, 128x128) using pure Python standard library (struct + zlib).
Creates a referee whistle / scale icon with dark sports aesthetic.
"""

import os
import struct
import zlib


def create_png(width, height, get_pixel_rgba):
    raw_bytes = bytearray()
    for y in range(height):
        raw_bytes.append(0)  # filter type 0 (None)
        for x in range(width):
            r, g, b, a = get_pixel_rgba(x, y, width, height)
            raw_bytes.extend([r, g, b, a])

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress(bytes(raw_bytes), 9))
    iend = chunk(b"IEND", b"")

    return header + ihdr + idat + iend


def referee_icon_pixel(x, y, w, h):
    # Normalized coords from -1 to 1
    nx = (x - w / 2) / (w / 2)
    ny = (y - h / 2) / (h / 2)
    dist = (nx * nx + ny * ny) ** 0.5

    # Rounded background badge (Warm Beige & Deep Forest Green)
    if dist > 0.95:
        return (0, 0, 0, 0)  # transparent
    elif dist > 0.88:
        # outer border ring (deep forest green)
        return (27, 67, 50, 245)
    elif dist > 0.82:
        # inner accent ring (sage green)
        return (82, 183, 136, 255)
    else:
        # Background: warm beige
        bg = (244, 241, 234, 255)

        # Scale / Balance symbol in center (forest green)
        fg = (27, 67, 50, 255)

        # Center post
        if abs(nx) < 0.12 and -0.6 < ny < 0.45:
            return fg
        # Base
        if abs(nx) < 0.45 and 0.4 <= ny <= 0.6:
            return fg
        # Crossbar
        if abs(nx) < 0.65 and -0.45 <= ny <= -0.32:
            return fg
        # Left balance pan (warm ochre gold)
        if -0.7 < nx < -0.35 and -0.32 < ny < 0.05:
            if abs(nx - (-0.52)) < 0.08 or (ny > -0.02 and abs(nx - (-0.52)) < 0.18):
                return (184, 146, 48, 255)
        # Right balance pan (deep pitch green)
        if 0.35 < nx < 0.7 and -0.32 < ny < 0.05:
            if abs(nx - 0.52) < 0.08 or (ny > -0.02 and abs(nx - 0.52) < 0.18):
                return (45, 106, 79, 255)

        return bg


def main():
    icons_dir = os.path.join(os.path.dirname(__file__), "extension", "icons")
    os.makedirs(icons_dir, exist_ok=True)

    sizes = [16, 48, 128]
    for size in sizes:
        png_data = create_png(size, size, referee_icon_pixel)
        filepath = os.path.join(icons_dir, f"icon{size}.png")
        with open(filepath, "wb") as f:
            f.write(png_data)
        print(f"Generated {filepath} ({size}x{size})")


if __name__ == "__main__":
    main()
