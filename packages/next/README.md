# Inter CJK for Next.js

## Installation

```bash
npm install inter-cjk
```

## Usage

```tsx
import { InterCJK } from "inter-cjk/font/sans";
// or
import { InterCJKDisplay } from "inter-cjk/font/display";
// or both
import { InterCJK, InterCJKDisplay } from "inter-cjk/font";

export default function RootLayout({ children }) {
  return (
    <html className={`${InterCJK.variable} ${InterCJKDisplay.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

## Tailwind CSS

```js
// tailwind.config.js
module.exports = {
  theme: {
    fontFamily: {
      sans: ["var(--font-inter-cjk)", "sans-serif"],
      display: ["var(--font-inter-cjk-display)", "sans-serif"],
    },
  },
};
```

## CSS Variables

| Variable | Font |
|----------|------|
| `--font-inter-cjk` | Inter CJK (text, opsz=14) |
| `--font-inter-cjk-display` | Inter CJK Display (display, opsz=32) |
