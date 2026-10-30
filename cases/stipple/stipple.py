# 실버 고스트 사진을 점묘 점 좌표로 바꾼다. 밝은 곳과 윤곽선에 점이 몰린다.
import json, sys, numpy as np
from PIL import Image, ImageFilter
from scipy.spatial import cKDTree
src, mask_p, out, N = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
W = 1280
img = Image.open(src).convert('L'); H = round(img.height * W / img.width)
img = img.resize((W, H), Image.LANCZOS)
m = np.asarray(Image.open(mask_p).convert('L').resize((W, H), Image.LANCZOS), float) / 255
lum = np.asarray(img, float) / 255
from scipy import ndimage
g = ndimage.gaussian_filter(lum, 1.1)
edge = np.hypot(ndimage.sobel(g, 1), ndimage.sobel(g, 0)); edge = np.clip(edge / np.percentile(edge[m > 0.5], 97), 0, 1)
den = m * (0.015 + 0.45 * lum ** 2.4 + 2.6 * edge ** 1.3)
den[m < 0.5] = 0
p = den.ravel() / den.sum()
rng = np.random.default_rng(7)
idx = rng.choice(den.size, N, p=p)
pts = np.c_[idx % W, idx // W].astype(float) + rng.random((N, 2))
# 가중 Lloyd 몇 번: 점이 고르게 퍼져 덩어리가 안 생긴다
S = rng.choice(den.size, N * 12, p=p)
samp = np.c_[S % W, S // W].astype(float) + rng.random((N * 12, 2))
for _ in range(3):
    _, near = cKDTree(pts).query(samp)
    cnt = np.bincount(near, minlength=N)
    sx = np.bincount(near, samp[:, 0], N); sy = np.bincount(near, samp[:, 1], N)
    ok = cnt > 0
    pts[ok, 0] = sx[ok] / cnt[ok]; pts[ok, 1] = sy[ok] / cnt[ok]
xi = np.clip(pts[:, 0].astype(int), 0, W - 1); yi = np.clip(pts[:, 1].astype(int), 0, H - 1)
b = lum[yi, xi]; e = edge[yi, xi]
x0, x1 = pts[:, 0].min(), pts[:, 0].max(); y0, y1 = pts[:, 1].min(), pts[:, 1].max()
sc = 2 / (x1 - x0)
nx = (pts[:, 0] - (x0 + x1) / 2) * sc; ny = (pts[:, 1] - (y0 + y1) / 2) * sc
flat = []
for a, c, d, f in zip(nx, ny, b, e):
    flat += [round(a * 1000), round(c * 1000), round(d * 99), round(f * 99)]
json.dump({'n': N, 'aspect': round((y1 - y0) / (x1 - x0), 4), 'p': flat}, open(out, 'w'), separators=(',', ':'))
print(N, 'points', round((y1 - y0) / (x1 - x0), 3))
