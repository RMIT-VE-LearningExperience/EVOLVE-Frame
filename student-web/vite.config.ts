import { sites } from '@openai/sites-vite-plugin';
import tailwindcss from '@tailwindcss/postcss';
import vinext from 'vinext';
import { defineConfig } from 'vite';

// This explorer has no server or storage bindings. Use static output and avoid
// starting a local Workers runtime during static prerendering on Windows.
export default defineConfig({
  css: { postcss: { plugins: [tailwindcss()] } },
  plugins: [vinext(), sites()],
  server: { host: '127.0.0.1' },
});
