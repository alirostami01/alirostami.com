# Self-hosted performance dependencies

These browser assets replace runtime requests to jsDelivr. They were copied from
exact npm package releases; each package's upstream license is stored beside its
asset.

| Local asset | npm package and version | Upstream file |
|---|---|---|
| `fontawesome/all.min.css` + `webfonts/*` | `@fortawesome/fontawesome-free@6.1.1` | `css/all.min.css`, `webfonts/*` |
| `animate/animate-subset.min.css` | `animate.css@4.1.1` | custom subset of `animate.css` |
| `autocomplete/autocomplete.min.js` | `autocomplete.js@0.38.1` | `dist/autocomplete.min.js` |
| `lunr/lunr.min.js` | `lunr@2.3.9` | `lunr.min.js` |
| `clipboard/clipboard.min.js` | `clipboard@2.0.11` | `dist/clipboard.min.js` |
| `sharer/sharer.min.js` | `sharer.js@0.5.1` | `sharer.min.js` |
| `typeit/index.umd.js` | `typeit@8.6.0` | `dist/index.umd.js` |

Two deliberate transformations are applied:

1. Font Awesome's `font-display:block` declarations are changed to
   `font-display:swap` so icons cannot indefinitely hide while webfonts load.
2. The Animate.css bundle contains only the animations used by LoveIt and the
   checked-in pages: `flash`, `pulse`, `fadeIn`, `fadeInDown`, `fadeOut`,
   `fadeOutUp`, and `flipInX`, plus Animate.css's reduced-motion rule.

`clipboard.min.js` is retained for generator output that contains LoveIt's
`.highlight > .chroma` copy controls, but the current site has no such markup and
therefore does not request it. `scripts/update-performance.py` decides which
JavaScript dependencies each page receives from its actual DOM features.

Run `python3 scripts/check-performance.py` after updating an asset. The checker
pins the expected SHA-256 digests, validates licenses and local references, and
will require an intentional digest update when a vendor file changes.
