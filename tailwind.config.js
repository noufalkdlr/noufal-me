/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./App.{js,jsx,ts,tsx}",
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Geist-Regular"],
        Medium: ["Geist-Medium"],
        SemiBold: ["Geist-SemiBold"],
        bold: ["Geist-Bold"],
        black: ["Geist-Black"],

      },
    },
  },
  plugins: [],
};
