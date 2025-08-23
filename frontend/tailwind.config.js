/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/ui/**/*.{js,ts,jsx,tsx,mdx}',
    './src/shared/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          100: '#e6efff',
          500: '#1a4aa6',
          600: '#003087', // 핵심 브랜드 컬러
          700: '#002766',
          900: '#001a4d',
        },
        gray: {
          100: '#f1f5f9',
          300: '#cbd5e1',
          500: '#64748b',
          700: '#334155',
          900: '#0b1220',
        },
        success: '#16a34a',
        warning: '#f59e0b',
        danger:  '#dc2626',
        info:    '#2563eb',
      },
      borderRadius: {
        brand: '12px',
      },
      boxShadow: {
        soft: '0 4px 8px rgba(0,0,0,0.06)',
      },
      spacing: {
        'section': '24px',
      },
    },
  },
  plugins: [],
}