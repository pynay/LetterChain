/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./src/**/*.{js,ts,jsx,tsx}",
      "./src/app/**/*.{js,ts,jsx,tsx}",
      "./src/components/**/*.{js,ts,jsx,tsx}",
    ],
    safelist: [
      "btn-primary",
      "btn-accent",
      "bg-white",
      "text-navy-blue",
      "text-slate-gray",
      "text-emerald-green",
    ],
    theme: {
      extend: {
        colors: {
          'navy-blue': '#1A1A40',
          'slate-gray': '#6C757D',
          'white': '#FFFFFF',
          'emerald-green': '#2ECC71',
        },
      },
    },
    plugins: [],
  };