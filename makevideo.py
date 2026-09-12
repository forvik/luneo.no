"""Lager en original, sømløst loopende bakgrunnsfilm: mørk grunn med myke
magenta/lilla glødflater og noen avrundede neonlinjer som driver sakte.
Farger hentet fra Luneo-profilen (#1B222D grunn, #C010C5 aksent)."""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1280, 720
FPS = 24
SEC = 14
N = FPS * SEC
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frames')
os.makedirs(OUT, exist_ok=True)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
xx /= W; yy /= H

BASE = np.array([0x1B, 0x22, 0x2D], np.float32)
MAG = np.array([0xC0, 0x10, 0xC5], np.float32)
VIO = np.array([0x6A, 0x1F, 0xB8], np.float32)
BLUE = np.array([0x2A, 0x3C, 0x8C], np.float32)

# glødflater: (farge, senterbane, radius, styrke, fase)
blobs = [
    (MAG, (0.78, 0.35), 0.16, 0.10, 0.42, 0.0),
    (VIO, (0.25, 0.75), 0.20, 0.09, 0.38, 1.7),
    (BLUE, (0.55, 0.15), 0.22, 0.08, 0.35, 3.1),
    (MAG, (0.15, 0.25), 0.12, 0.07, 0.35, 4.4),
]

def frame(i):
    t = i / N * 2 * math.pi  # én full periode = sømløs loop
    img = np.tile(BASE, (H, W, 1))
    for col, (cx, cy), ax, ay, rad, ph in blobs:
        x = cx + ax * math.sin(t + ph)
        y = cy + ay * math.cos(t * 1.0 + ph * 0.7)
        d2 = ((xx - x) ** 2 * 1.6 + (yy - y) ** 2) / (rad ** 2)
        g = np.exp(-d2)[..., None]
        img = img + (col - BASE) * g * 0.42
    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

    # neonlinjer: avrundede kurver som driver over flaten
    lines = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(lines)
    for k in range(4):
        ph = k * 1.3
        pts = []
        for s in range(0, 41):
            u = s / 40
            x = (u * 1.4 - 0.2 + 0.05 * math.sin(t + ph)) * W
            y = (0.2 + 0.18 * k + 0.09 * math.sin(u * 4 + t * (1 if k % 2 else -1) + ph)) * H
            pts.append((x, y))
        c = (192, 16, 197) if k % 2 == 0 else (140, 60, 220)
        d.line(pts, fill=c, width=6, joint='curve')
    glow = lines.filter(ImageFilter.GaussianBlur(26))
    core = lines.filter(ImageFilter.GaussianBlur(3))
    g = np.asarray(glow).astype(np.float32) * 0.55 + np.asarray(core).astype(np.float32) * 0.3
    out = np.clip(np.asarray(base).astype(np.float32) + g, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(OUT, f'f{i:04d}.png'))

for i in range(N):
    frame(i)
    if i % 48 == 0:
        print('frame', i, '/', N, flush=True)

subprocess.run([
    'ffmpeg', '-y', '-framerate', str(FPS), '-i', os.path.join(OUT, 'f%04d.png'),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.0',
    '-preset', 'slow', '-crf', '30', '-movflags', '+faststart', '-an',
    os.path.join(os.path.dirname(OUT), 'site', 'img', 'bakgrunn.mp4')
], check=True)
# plakatbilde (første frame) for rask visning
Image.open(os.path.join(OUT, 'f0000.png')).convert('RGB').save(
    os.path.join(os.path.dirname(OUT), 'site', 'img', 'bakgrunn.jpg'), quality=80)
print('done')
