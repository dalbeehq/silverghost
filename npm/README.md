# Silver Ghost

Motion made by AI. A human watched every one before it went in.

Made By Opus 5.5, Curated by HUMAN.

Every item ships with the version we threw away and one line on why. You see what got cut, not only what survived.

Browse: https://thedalbee.com/silverghost

## Use

```
npx silverghost list
npx silverghost add silver-ghost
```

`add` writes two files into `./silverghost/` (change it with `--dir`). You own the copies.

- `<name>.html` is a standalone page. Open it directly.
- `<name>.js` defines a `<silverghost-<name>>` tag you can drop into any page:

```html
<script type="module" src="./silverghost/glass-blob-text.js"></script>
<silverghost-glass-blob-text style="width: 640px"></silverghost-glass-blob-text>
```

The tag runs the page inside an iframe in a shadow root, so its styles never touch yours. It keeps a 16:9 box unless you size it. No build step. The whale items load three.js r128 from cdnjs.

The registry follows the shadcn registry format: `https://thedalbee.com/silverghost/registry.json`. Set `SILVERGHOST_REGISTRY` to a URL or a local folder to use another registry.

## Items

| Kind | Items |
|---|---|
| Stipple (weighted Voronoi) | silver-ghost, apollo-eagle |
| Shader (WebGL2) | glass-blob-text, prism-dispersion, glass-panel-video, mouse-scroll-lens, film-grain-halation, hangul-title-glass, liquid-metal, fluted-glass, glass-torus-raymarch, light-leak-bloom |
| Point cloud and ASCII (three.js) | whale-1-lens, whale-2-surface, whale-3-points |
| From an uploaded video (GSAP) | capture-underline |

## Layout

- `items/<name>/` holds `item.json`, the kept `<name>.html`, `poster.jpg`, and `rejected/` with the cut version.
- `cases/stipple/make.sh <photo> <name> <title> <credit>` turns a photo into a stipple page.
- `tools/build.py` builds `dist/registry.json` and `dist/r/<name>.json`. It fails when an item has no rejected version.
- `npm/` is the `silverghost` CLI.

## License

Code is MIT. The photos in the stipple items are public domain (Wikimedia Commons, NASA). Credits are on each page.

Made by [dalbee](https://thedalbee.com).
