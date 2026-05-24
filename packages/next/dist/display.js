const localFont = require("next/font/local");

const InterCJKDisplay = localFont.default({
  src: "./fonts/InterCJKDisplayVariable.woff2",
  variable: "--font-inter-cjk-display",
  weight: "100 900",
  display: "swap",
  adjustFontFallback: "Arial",
});

module.exports = { InterCJKDisplay };
