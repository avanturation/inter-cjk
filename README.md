# Inter CJK

Inter CJK는 [Inter](https://rsms.me/inter)와 [Pretendard](https://github.com/orioncactus/pretendard)를 결합하고, UI 등 주요 사용 환경에 맞게 보정해 한국어, 일본어, 중국어까지 커버하는 서체입니다. Inter와 Pretendard가 지원하는 모든 OpenType 기능을 그대로 포함하며, 9가지 굵기와 가변 (Variable) 글꼴을 지원합니다.

[최신 버전 다운로드하기](https://github.com/avanturation/inter-cjk/releases/tag/v1.0.0)

<br/>

![overview](docs/overview.png)

<br/>

## 도대체 왜

<br/>

![why](docs/why.png)

<br/>

Pretendard는 다국어를 폭넓게 지원해 UI에서 범용 서체로 쓰기 좋지만, 영미권 텍스트의 가독성이나 `@`, `[`, `(`와 같은 기호 디테일까지 고려하면 Inter가 더 적합합니다. 또한 40px 이상의 Hero 문구에서는 시인성을 위해 Inter Display를 사용합니다—Pretendard는 Display용 optical size를 제공하지 않아 Hero에서의 시인성 확보가 어렵기 때문입니다. 다만 Inter는 CJK를 지원하지 않아 한국 · 일본 · 중국어가 포함된 환경에선 단독으로 쓰기 어렵습니다.

Inter CJK는 이를 해결하고자 Pretendard JP의 CJK 글리프를 Inter에 결합하고, `calt` 피처 보완 · Line Height 조정 · Figma 등 상용 디자인 툴에서의 UI 설계 시 호환성까지 보완하며 Pretendard의 설계 원칙은 유지하였고, Inter의 라틴 품질을 그대로 살렸습니다.

# Inter CJK 사용하기

[최신 버전 다운로드하기](https://github.com/avanturation/inter-cjk/releases/tag/v1.0.0)

## 웹 폰트로 사용하기

### Variable (권장)

```html
<link href="https://cdn.jsdelivr.net/npm/inter-cjk/dist/web/inter-cjk.css" rel="stylesheet">
```

### Dynamic Subset (경량 로딩)

페이지에서 실제로 사용하는 글리프만 로드합니다. CJK 폰트의 용량 문제를 해결합니다.

```html
<link href="https://cdn.jsdelivr.net/npm/inter-cjk/dist/web/dynamic-subset/inter-cjk-variable-dynamic-subset.css" rel="stylesheet">
```

### 개별 Weight (Static)

특정 굵기만 필요한 경우:

```html
<link href="https://cdn.jsdelivr.net/npm/inter-cjk/dist/web/InterCJK-Regular.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/inter-cjk/dist/web/InterCJK-Bold.css" rel="stylesheet">
```

## Next.js에서 사용하기

```bash
npm install inter-cjk
```

```tsx
// app/layout.tsx
import { InterCJK, InterCJKDisplay } from "inter-cjk/font";

export default function RootLayout({ children }) {
  return (
    <html className={`${InterCJK.variable} ${InterCJKDisplay.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

```css
/* globals.css */
body {
  font-family: var(--font-inter-cjk), sans-serif;
}

h1, h2, h3 {
  font-family: var(--font-inter-cjk-display), sans-serif;
}
```

개별 import도 가능합니다:

```tsx
import { InterCJK } from "inter-cjk/font/sans";
import { InterCJKDisplay } from "inter-cjk/font/display";
```

## font-family

권장하는 `font-family` 조합은 아래와 같습니다.

```css
font-family: "Inter CJK Variable", "Inter CJK",
  -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo",
  "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", sans-serif,
  "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
```

## Display 사용하기

Inter CJK Variable은 하나의 파일에 Text(opsz=14)와 Display(opsz=32)를 모두 포함합니다.

```css
/* 본문 (기본, opsz=14) */
body {
  font-family: "Inter CJK Variable", sans-serif;
}

/* 제목/Hero (opsz=32) */
h1 {
  font-family: "Inter CJK Variable", sans-serif;
  font-variation-settings: 'opsz' 32;
}
```

Static 폰트에서는 별도 패밀리로 분리되어 있습니다:
- `Inter CJK` — 본문용
- `Inter CJK Display` — 제목용

# Font Families

- **Inter CJK** — UI, 본문에 최적화 (optical size 14)
- **Inter CJK Display** — Display, Hero에 최적화 (optical size 32)

## Variable Axes

| Axis | Tag | Range | Default |
|------|-----|-------|---------|
| Optical Size | `opsz` | 14–32 | 14 |
| Weight | `wght` | 100–900 | 400 |

## 언어 커버리지

- 라틴, 키릴, 그리스 문자 계열 (Inter 기반)
- 11,172자 한글 음절 (Pretendard 기반)
- 184자 히라가나 + 가타카나 (Pretendard 기반)
- 7,138자 CJK 통합 한자 (Pretendard 기반)
- CJK 기호·호환·반각/전각 문자 (Inter & Pretendard 혼합)

## 디자인 원칙

[Pretendard](https://cactus.tistory.com/306)의 제작 비하인드와 [SUIT](https://sun.fo/suit/)의 디자인 원칙을 참고했습니다.

- **수직 정렬**: CJK 글리프 중심을 라틴 Cap height 중심에 맞춤
- **회색도 매칭**: CJK 획을 1% 얇게 조정해 라틴과 시각적 굵기 균형
- **광학 크기**: Display(opsz=32)에서 CJK 3% 축소
- **컨텍스트 기호 정렬**: 한글 인접 시 `@`, `→`, `-` 등 49개 기호가 자동으로 높이 조정 (`rclt`)
- **Vertical Metrics**: Line Height ratio 1.125 (12→14, 14→16, 16→18, 18→20px 짝수)
- **₩ 원화 기호**: Pretendard JP의 한국식 글리프 사용

## OpenType Features

Inter CJK는 Inter와 Pretendard가 지원하는 모든 OpenType 기능들을 지원합니다.

`calt` `ccmp` `case` `dlig` `frac` `sups` `subs` `sinf` `dnom` `numr` `tnum` `zero` `cpsp` `kern` `mark` `mkmk`

Stylistic Sets:
- `ss01` Straight-sided six and nine
- `ss02` Open four
- `ss03` Centered colon
- `ss05` Korean localization (contextual ellipsis)
- `ss06` Enhanced readability / Disambiguation
- `ss07` Single-storey a
- `ss08` Straight three

Character Variants: `cv01`–`cv14`

# Build

Inter와 Pretendard의 원본 소스를 `git submodule`로 연결해 최신 버전으로 빌드한 후, Inter CJK 설계 원칙에 맞는 패치를 진행해 빌드합니다.

```bash
python3 -m pip install -r requirements.txt
make clean
make all
```

# Credits

- [Inter](https://rsms.me/inter/) by @rsms
- [Pretendard](https://github.com/orioncactus/pretendard) by @orioncactus

## Contribute

Inter CJK는 UI 디자이너로서 평소 가지고 있던 생각들을 조합해, `Glyphs`와 같은 서체 전용 툴 없이 OpenCode 만으로 제작되었습니다. 

폰트에 대한 지식이 부족한 만큼, 오픈소스 커뮤니티의 많은 피드백과 기여가 필요합니다. Issues와 Pull Request를 통해 기여해주시면 감사하겠습니다.

## License

[SIL Open Font License 1.1](LICENSE.txt)
