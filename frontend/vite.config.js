import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'    // ← ¡imprescindible!
console.log('VITE CONFIG CARGADA. @ →', path.resolve(__dirname, 'src'));
import svgLoader from 'vite-svg-loader'

export default defineConfig({
  plugins: [vue(), svgLoader()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
