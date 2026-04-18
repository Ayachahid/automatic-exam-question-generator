/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#D97757',
          hover: '#C4633F',
          light: '#E8A48E',
          faint: '#FDF0EB',
          ring: 'rgba(217, 119, 87, 0.15)',
        },
        accent: {
          blue: '#5B8DB8',
          green: '#6B8B4F',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          secondary: '#F7F6F3',
          tertiary: '#EFEEEB',
          border: '#E5E3DE',
          'border-hover': '#D4D1CB',
        },
        background: {
          DEFAULT: '#FDFDFC',
        },
        text: {
          main: '#1A1918',
          secondary: '#3D3C39',
          muted: '#8C8A84',
          faint: '#B5B3AD',
        },
        success: {
          DEFAULT: '#6B8B4F',
          bg: '#F2F6EE',
          border: '#D9E5CF',
          text: '#4A6B33',
        },
        danger: {
          DEFAULT: '#C4633F',
          bg: '#FDF0EB',
          border: '#F0D4C7',
          text: '#A04E2E',
        },
      },
      borderRadius: {
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '20px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.04)',
        'md': '0 2px 8px rgba(0, 0, 0, 0.06)',
        'lg': '0 4px 16px rgba(0, 0, 0, 0.08)',
        'card': '0 1px 3px rgba(0, 0, 0, 0.04), 0 0 0 1px rgba(0, 0, 0, 0.02)',
      },
      keyframes: {
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'spin-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'slide-up': 'slide-up 0.35s ease-out',
        'fade-in': 'fade-in 0.3s ease-out',
        'spin-slow': 'spin-slow 2s linear infinite',
      },
    },
  },
  plugins: [],
}
