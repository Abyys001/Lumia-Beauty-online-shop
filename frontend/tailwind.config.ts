import type { Config } from 'tailwindcss'
import daisyui from 'daisyui'

export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Vazirmatn Variable"', 'Vazirmatn', 'Tahoma', 'sans-serif'],
      },
      colors: {
        lumia: {
          gold: '#C9A96E',
          cream: '#F5F0EB',
          warm: '#8B6F5C',
          dark: '#2D2A26',
          light: '#FDFBF9',
        },
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        lumia: {
          primary: '#C9A96E',
          'primary-content': '#2D2A26',
          secondary: '#F5F0EB',
          'secondary-content': '#2D2A26',
          accent: '#8B6F5C',
          'accent-content': '#FDFBF9',
          neutral: '#2D2A26',
          'neutral-content': '#FDFBF9',
          'base-100': '#FDFBF9',
          'base-200': '#F5F0EB',
          'base-300': '#E8E0D8',
          'base-content': '#2D2A26',
          info: '#3ABFF8',
          success: '#36D399',
          warning: '#FBBD23',
          error: '#F87272',
        },
      },
    ],
    darkTheme: false,
  },
} satisfies Config
