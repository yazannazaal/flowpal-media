"""Download images listed in tools/images.txt and save them as optimized WebP."""
import io, pathlib, sys, urllib.request
from PIL import Image

root = pathlib.Path(__file__).resolve().parent.parent
out = root / "brands-sport" / "assets" / "img"
out.mkdir(parents=True, exist_ok=True)
for line in (root / "tools" / "images.txt").read_text().splitlines():
    if not line.strip():
        continue
    name, url = line.split()
    dest = out / f"{name}.webp"
    if dest.exists():
        continue
    data = urllib.request.urlopen(url, timeout=60).read()
    img = Image.open(io.BytesIO(data)).convert("RGB")
    max_side = 1000 if name.startswith(("p-", "g-")) else 1800
    img.thumbnail((max_side, max_side))
    img.save(dest, "WEBP", quality=82, method=6)
    print(name, img.size, dest.stat().st_size)
