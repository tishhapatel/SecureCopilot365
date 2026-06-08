import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#0a0d16',
        darkCard: '#121724',
        darkBorder: '#1f273b',
        cyberBlue: '#00d2ff',
        cyberPurple: '#9d4edd',
        cyberGreen: '#00f5d4'
      },
      boxShadow: {
        glow: '0 0 15px rgba(0, 210, 255, 0.25)',
        glowGreen: '0 0 15px rgba(0, 245, 212, 0.25)',
        glowPurple: '0 0 15px rgba(157, 78, 221, 0.25)'
      }
    },
  },
  plugins: [],
}

export default config;
