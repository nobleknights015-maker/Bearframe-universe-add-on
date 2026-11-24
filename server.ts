import express from 'express';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DOWNLOADS_DIR = path.resolve(__dirname, 'public', 'downloads');
const ALLOWED_FILES = new Set([
  'Bearframe_Bedrock_0.4.1.mcaddon',
  'Bearframe_Bedrock_0.4.0.mcaddon',
  'Bearframe_Behavior_0.4.0.mcpack',
  'Bearframe_Resources_0.4.0.mcpack',
  'Bearframe_Bedrock_Source_0.4.0.zip',
  'Bearframe_Bedrock.gitbundle',
]);

async function startServer() {
  const app = express();
  const PORT = 3000;

  const serveAttachment = (req: express.Request, res: express.Response) => {
    const filename = path.basename(req.params.filename || '');
    if (!ALLOWED_FILES.has(filename)) {
      res.status(404).json({ error: 'Artifact not found' });
      return;
    }
    const filePath = path.join(DOWNLOADS_DIR, filename);
    if (!fs.existsSync(filePath)) {
      res.status(404).json({ error: 'Artifact not built yet' });
      return;
    }
    const stat = fs.statSync(filePath);
    // Force exact binary attachment headers so Android Chrome saves the true
    // .mcaddon / .mcpack filename without rendering in Chrome or renaming to .txt/.zip.
    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Content-Length', String(stat.size));
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Cache-Control', 'no-store');
    fs.createReadStream(filePath).pipe(res);
  };

  app.get('/api/download/:filename', serveAttachment);
  app.get('/downloads/:filename', serveAttachment);

  if (process.env.NODE_ENV !== 'production') {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distDir = path.resolve(__dirname, 'dist');
    app.use(express.static(distDir));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distDir, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Bearframe Release Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
