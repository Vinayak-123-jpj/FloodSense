/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        survey: {
          paper: '#F2EEE4',
          card: '#FAF7F0',
          ink: '#14202B',
          slate: '#4A5568',
          teal: '#1F6B75',
          ochre: '#C88A2E',
          border: '#D8D2C2'
        },
        night: {
          bg: '#0C141B',
          card: '#131E28',
          text: '#E6E1D5',
          slate: '#94A3B8',
          teal: '#2B8C98',
          border: '#1F2D3A'
        },
        risk: {
          green: '#2E7D32',
          yellow: '#D97706',
          orange: '#EA580C',
          red: '#DC2626'
        }
      },
      fontFamily: {
        serif: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Inter Tight', 'Instrument Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'IBM Plex Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
