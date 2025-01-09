export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#6366f1',
        'secondary': '#4f46e5',
        'accent': '#818cf8',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
