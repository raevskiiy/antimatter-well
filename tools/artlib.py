"""Tiny procedural painting helpers. All coordinates are in *normal-resolution* pixels (32 px = 1 tile);
the canvas is rendered at R times that and downsampled at the end."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

R = 4  # supersampling factor relative to normal resolution


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def shade(c, f):
    """f<1 darker, f>1 lighter."""
    if f <= 1:
        return tuple(int(v * f) for v in c[:3]) + tuple(c[3:])
    return tuple(int(v + (255 - v) * (f - 1)) for v in c[:3]) + tuple(c[3:])


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * R, h * R), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    # --- primitives -----------------------------------------------------
    def _s(self, v):
        return [int(round(x * R)) for x in v]

    def rect(self, box, fill=None, outline=None, width=1):
        self.d.rectangle(self._s(box), fill=fill, outline=outline, width=int(width * R))

    def rrect(self, box, r, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(self._s(box), radius=int(r * R), fill=fill, outline=outline, width=int(width * R))

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.d.ellipse(self._s(box), fill=fill, outline=outline, width=int(width * R))

    def poly(self, pts, fill=None, outline=None):
        flat = [(int(round(x * R)), int(round(y * R))) for x, y in pts]
        self.d.polygon(flat, fill=fill, outline=outline)

    def line(self, pts, fill, width=1):
        flat = [(int(round(x * R)), int(round(y * R))) for x, y in pts]
        self.d.line(flat, fill=fill, width=max(1, int(width * R)))

    # --- gradients ------------------------------------------------------
    def grad(self, box, c1, c2, horizontal=False, shape="rect", r=0, lumpy=0.0, pts=None):
        """Fill `box` with a linear gradient c1->c2 using a rect / rrect / ellipse mask."""
        x0, y0, x1, y1 = [int(round(v * R)) for v in box]
        gw, gh = max(1, x1 - x0), max(1, y1 - y0)
        t = np.linspace(0, 1, gw if horizontal else gh)
        arr = np.zeros((gh, gw, 4), dtype=np.uint8)
        for ch in range(4):
            a = c1[ch] if ch < len(c1) else 255
            b = c2[ch] if ch < len(c2) else 255
            vals = a + (b - a) * t
            if horizontal:
                arr[:, :, ch] = vals[None, :]
            else:
                arr[:, :, ch] = vals[:, None]
        layer = Image.fromarray(arr, "RGBA")
        mask = Image.new("L", (gw, gh), 0)
        md = ImageDraw.Draw(mask)
        if shape == "rect":
            md.rectangle([0, 0, gw - 1, gh - 1], fill=255)
        elif shape == "poly":
            md.polygon([(int(round(px * R)) - x0, int(round(py * R)) - y0) for px, py in pts], fill=255)
        elif shape == "rrect":
            md.rounded_rectangle([0, 0, gw - 1, gh - 1], radius=int(r * R), fill=255)
        else:
            md.ellipse([0, 0, gw - 1, gh - 1], fill=255)
        base_alpha = layer.split()[3]
        mask = ImageChops_multiply(mask, base_alpha)
        self.img.paste(layer, (x0, y0), mask)

    def glow(self, cx, cy, r, color, strength=1.0, power=2.0):
        size = max(2, int(r * 2 * R))
        m = Image.radial_gradient("L").resize((size, size), Image.BICUBIC)
        m = ImageOps.invert(m)
        lut = [int(255 * ((v / 255.0) ** power) * min(1.0, strength)) for v in range(256)]
        m = m.point(lut)
        layer = Image.new("RGBA", (size, size), tuple(color[:3]) + (255,))
        self.img.alpha_composite(self._pad(layer, m, int(cx * R - size / 2), int(cy * R - size / 2)))

    def _pad(self, layer, mask, x, y):
        full = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        layer = layer.copy()
        layer.putalpha(mask)
        full.paste(layer, (x, y))
        return full

    def blur_layer(self, drawfn, radius):
        """Draw something on a temp layer, blur it and composite (soft shadows, bloom)."""
        tmp = Canvas(self.w, self.h)
        drawfn(tmp)
        blurred = tmp.img.filter(ImageFilter.GaussianBlur(radius * R))
        self.img.alpha_composite(blurred)

    def noise(self, box, amount=10, seed=1):
        """Subtle speckle inside the already painted pixels of box."""
        x0, y0, x1, y1 = [int(round(v * R)) for v in box]
        rnd = np.random.RandomState(seed)
        region = np.array(self.img.crop((x0, y0, x1, y1))).astype(np.int16)
        n = rnd.randint(-amount, amount + 1, size=region.shape[:2])
        n = np.array(Image.fromarray((n + 128).astype(np.uint8)).filter(ImageFilter.GaussianBlur(R * 0.6))).astype(np.int16) - 128
        for ch in range(3):
            region[:, :, ch] = np.clip(region[:, :, ch] + n, 0, 255)
        out = Image.fromarray(region.astype(np.uint8), "RGBA")
        self.img.paste(out, (x0, y0))

    # --- output ---------------------------------------------------------
    def save(self, path, scale):
        """scale=1 -> w x h, scale=2 -> HR (2w x 2h). Premultiplied resize avoids dark fringes."""
        size = (self.w * scale, self.h * scale)
        im = self.img.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")
        im.save(path)

    def final(self, scale):
        size = (self.w * scale, self.h * scale)
        return self.img.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")


def ImageChops_multiply(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)


def fit_icon(img, size=64, pad=3):
    """Crop to the painted area and scale into a size x size icon."""
    bbox = img.getbbox()
    crop = img.crop(bbox)
    w, h = crop.size
    s = min((size - 2 * pad) / w, (size - 2 * pad) / h)
    nw, nh = max(1, int(w * s)), max(1, int(h * s))
    crop = crop.convert("RGBa").resize((nw, nh), Image.LANCZOS).convert("RGBA")
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(crop, ((size - nw) // 2, (size - nh) // 2))
    return out
