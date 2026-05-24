const localFont = require("next/font/local");

const InterCJK = localFont.default({
  src: "./fonts/InterCJKVariable.woff2",
  variable: "--font-inter-cjk",
  weight: "100 900",
  display: "swap",
  fallback: [
    "-apple-system", "BlinkMacSystemFont", "Apple SD Gothic Neo",
    "Segoe UI", "Roboto", "Helvetica Neue", "Noto Sans", "sans-serif",
  ],
});

module.exports = { InterCJK };
