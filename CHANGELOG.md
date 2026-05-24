# Changelog

## 0.1.0 (2025-05-24)

Initial pre-release.

### Font
- Merged Inter Variable (opsz + wght) with Pretendard JP Variable (wght)
- CJK vertical alignment: Y offset +21 (matches Pretendard's 가-H center diff)
- CJK weight matching: 1% horizontal thinning for gray-level balance
- CJK optical size: 3% tighter at opsz=32 (Display)
- ₩ (Won sign) replaced with Pretendard JP's Korean-style glyph
- `rclt` feature: 49 symbols contextually switch to .case when adjacent to CJK
- Vertical metrics: ratio 1.125, symmetric around cap center (asc=1897, desc=-407)
- Line height even at 12/14/16/18px in Figma
- Inter Display glyphs used for Display variant (via opsz instancer)

### OpenType
- All Inter features preserved (calt, ccmp, case, dlig, frac, tnum, zero, cv01-16, ss01-08)
- Added `rclt` for CJK contextual symbol alignment
- CJK scripts registered in GSUB/GPOS (hang, kana, hani)

### Distribution
- Variable TTF: InterCJKVariable.ttf, InterCJKDisplayVariable.ttf
- Static TTF: 9 weights × 2 families = 18 files
- Web: woff2 (variable + static) + dynamic subset (119 splits × 2)
- CSS: @font-face with local() fallback + @font-feature-values
- npm: `inter-cjk` package with jsDelivr CDN support

### Build
- Source: Inter (git submodule) + Pretendard JP (release download)
- Pipeline: fontmake → merge (build-full.py) → split-opsz → gen-static → woff2 → dynamic-subset
- Reproducible: `make all` from clean clone
