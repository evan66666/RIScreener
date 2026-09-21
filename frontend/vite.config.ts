import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import http from 'node:http'

let currentBackend = 'http://127.0.0.1:8000'

function checkPort(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get(`http://127.0.0.1:${port}/api/health`, { timeout: 400 }, (res) => {
      resolve(res.statusCode === 200)
    })
    req.on('error', () => resolve(false))
    req.on('timeout', () => {
      req.destroy()
      resolve(false)
    })
  })
}

async function detectBackend() {
  if (await checkPort(8000)) {
    currentBackend = 'http://127.0.0.1:8000'
  }
}

detectBackend()
setInterval(detectBackend, 4000)

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        router: () => currentBackend,
        configure: (proxy: any) => {
          proxy.on('error', () => {
            detectBackend()
          })
        },
      } as any,
    },
  },
})

