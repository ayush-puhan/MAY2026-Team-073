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
    }
  }
})
