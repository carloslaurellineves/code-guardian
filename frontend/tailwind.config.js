/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'guardian-blue': '#87CEEB',
        'guardian-light-blue': '#B8E6E6',
        'guardian-white': '#FFFFFF',
        'guardian-gray': '#F5F5F5',
        'guardian-dark-gray': '#6B7280',
        'guardian-text': '#1F2937',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
