/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        crimson: '#A51C30',
        'crimson-dark': '#821626',
        cream: '#FDFCF8',
        charcoal: '#2E2E2E',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['"Libre Baskerville"', 'serif'],
      },
      backgroundImage: {
        'paper-texture': "url('https://www.transparenttextures.com/patterns/felt-paper.png')",
      }
    },
  },
  plugins: [],
}
