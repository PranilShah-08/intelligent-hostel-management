/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        display: ['"Space Grotesk"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        command: {
          950: '#060911',
          900: '#090d16',
          850: '#0c1322',
          800: '#0f172a',
          700: '#1e293b',
          600: '#334155',
        }
      }
    },
  },
  plugins: [],
}
