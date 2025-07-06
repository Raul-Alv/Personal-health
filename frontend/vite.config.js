import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'    // ← ¡imprescindible!
console.log('VITE CONFIG CARGADA. @ →', path.resolve(__dirname, 'src'));

export default defineConfig({
  plugins: [vue()],
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
        rewrite: p => p.replace(/^\/api/, '')
      }
    }
  }
})
