const localFont = require("next/font/local");

const InterCJK = localFont.default({
  src: "./fonts/InterCJKVariable.woff2",
  variable: "--font-inter-cjk",
  weight: "100 900",
  display: "swap",
  adjustFontFallback: "Arial",
});

module.exports = { InterCJK };
