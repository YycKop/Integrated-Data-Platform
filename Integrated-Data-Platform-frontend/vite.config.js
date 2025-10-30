// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8080, // 使用8080端口
    host: '0.0.0.0',
    strictPort: true, // 如果端口被占用则退出
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
