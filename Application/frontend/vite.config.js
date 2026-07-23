import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const useMock = env.VITE_USE_MOCK_BACKEND === 'true';

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@api': useMock 
          ? path.resolve(__dirname, './src/api/mockbackendApis') 
          : path.resolve(__dirname, './src/api/backendApis')
      }
    },
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          configure: (proxy, options) => {
            proxy.on('proxyRes', (proxyRes, req, res) => {
              proxyRes.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
              proxyRes.headers['Pragma'] = 'no-cache';
              proxyRes.headers['Expires'] = '0';
            });
          }
        }
      }
    }
  }
})
