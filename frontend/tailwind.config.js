/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        alfa: {
          red: '#EF3124',
          'red-hover': '#D42217',
          'red-light': '#FDF2F2',
          black: '#0B0E14',
          dark: '#1F2937',
          gray: '#8A94A6',
          'light-gray': '#F3F4F6',
          border: '#E5E7EB',
          surface: '#FFFFFF',
          bg: '#F8FAFC',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
