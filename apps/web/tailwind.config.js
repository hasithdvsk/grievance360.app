/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './apps/web/app/**/*.{js,ts,jsx,tsx,mdx}',
    './apps/web/components/**/*.{js,ts,jsx,tsx,mdx}',
    './apps/web/pages/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        obsidian: {
          950: '#050505',
          900: '#0a0a0c',
          850: '#111114',
          800: '#18181b',
        },
        slate: {
          950: '#020617',
        },
        kraft: {
          50: '#FAF6F0',
          100: '#F2E8D9',
          200: '#E4D3BC',
          300: '#D5BD9D',
          400: '#C8AD8D',
          500: '#B69772',
          600: '#9E7E5A',
          700: '#7E6345',
          800: '#523E2B',
          900: '#2A1E17',
          950: '#1C130E',
        },
        espresso: {
          700: '#3D2820',
          800: '#2C1D17',
          900: '#1F1410',
          950: '#140C0A',
        },
      },
      boxShadow: {
        'mono-glow': '0 0 35px -5px rgba(255,255,255,0.12)',
        'mono-card': '0 4px 20px -2px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.08)',
        'mono-card-hover': '0 12px 30px -4px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.22)',
        'mono-inset': 'inset 0 1px 1px 0 rgba(255,255,255,0.1)',
        'emboss': '4px 4px 10px rgba(0,0,0,0.15), -4px -4px 10px rgba(255,255,255,0.6)',
        'deboss': 'inset 3px 3px 6px rgba(0,0,0,0.25), inset -3px -3px 6px rgba(255,255,255,0.4)',
        'deboss-deep': 'inset 5px 5px 12px rgba(0,0,0,0.35), inset -4px -4px 10px rgba(255,255,255,0.2)',
        'card-stacked': '0 -10px 25px -5px rgba(0,0,0,0.15), 0 10px 20px -5px rgba(0,0,0,0.1)',
        'emboss-dark': '4px 4px 14px rgba(0,0,0,0.7), -2px -2px 8px rgba(255,255,255,0.06)',
        'deboss-dark': 'inset 3px 3px 6px rgba(0,0,0,0.8), inset -2px -2px 5px rgba(255,255,255,0.05)',
        'deboss-deep-dark': 'inset 5px 5px 14px rgba(0,0,0,0.9), inset -3px -3px 8px rgba(255,255,255,0.04)',
      },
      animation: {
        'shimmer': 'shimmer 2.5s infinite linear',
        'float-slow': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'mono-grid': 'linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
};
