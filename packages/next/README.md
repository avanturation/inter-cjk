# Inter CJK for Next.js

## 설치

```bash
npm install inter-cjk
```

## 사용법

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

개별 import도 가능:

```tsx
import { InterCJK } from "inter-cjk/font/sans";
import { InterCJKDisplay } from "inter-cjk/font/display";
```

## CSS에서 사용

```css
body {
  font-family: var(--font-inter-cjk), sans-serif;
}

h1, h2, h3 {
  font-family: var(--font-inter-cjk-display), sans-serif;
}
```

## CSS Variables

| Variable | 폰트 |
|----------|------|
| `--font-inter-cjk` | Inter CJK (본문, opsz=14) |
| `--font-inter-cjk-display` | Inter CJK Display (제목, opsz=32) |
