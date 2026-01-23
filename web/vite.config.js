import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5817,
    strictPort: true,  // 如果端口被占用，直接报错而不是切换到其他端口
    host: true
  },
  // 优化启动速度
  optimizeDeps: {
    include: ['vue', 'markdown-it']
  }
})
