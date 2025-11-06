/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        minarisBlue: "#004C97",
        minarisGray: "#F5F7FA",
      },
      fontFamily: {
        sans: ["Helvetica Neue", "Arial", "sans-serif"],
      },
      // --- smooth breathing + glow ---
      keyframes: {
        pulseGlow: {
          "0%, 100%": {
            transform: "scale(1)",
            opacity: "1",
            boxShadow: "0 0 8px rgba(116, 209, 255, 0.4)",
          },
          "50%": {
            transform: "scale(1.06)",
            opacity: "0.9",
            boxShadow: "0 0 20px rgba(116, 209, 255, 0.75)",
          },
        },
      },
      animation: {
        pulseGlow: "pulseGlow 3s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
