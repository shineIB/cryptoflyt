/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'crypto': {
          'dark': '#0a0a0f',
          'darker': '#050508',
          'card': '#12121a',
          'border': '#1e1e2e',
          'accent': '#8b5cf6',
          'accent-light': '#a78bfa',
          'green': '#22c55e',
          'red': '#ef4444',
          'yellow': '#eab308',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
