import { createRequire } from 'module';
const require = createRequire('/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
import { fileURLToPath } from 'url';
import path from 'path';
import http from 'http';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const server = http.createServer((req, res) => {
    let filePath = path.join(__dirname, req.url === '/' ? 'woonkamer.html' : req.url);
    const ext = path.extname(filePath);
    const types = { '.html': 'text/html', '.js': 'application/javascript' };

    let data;
    try { data = fs.readFileSync(filePath); } catch { res.writeHead(404); res.end(); return; }

    // Rewrite importmap for all HTML files
    if (ext === '.html') {
        let html = data.toString('utf-8');
        html = html.replace(
            /https:\/\/cdn\.jsdelivr\.net\/npm\/three@0\.160\.0\/build\/three\.module\.js/g,
            '/lib/three.module.js'
        );
        html = html.replace(
            /https:\/\/cdn\.jsdelivr\.net\/npm\/three@0\.160\.0\/examples\/jsm\//g,
            '/lib/'
        );
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(html);
        return;
    }

    res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
    res.end(data);
});
await new Promise(resolve => server.listen(0, resolve));
const port = server.address().port;

const browser = await chromium.launch({
    args: ['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
});

const rooms = [
    { file: 'bouwtekening.html', output: 'render_bouwtekening.png' },
];

for (const room of rooms) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 1100 } });
    page.on('console', msg => {
        if (msg.type() === 'error') console.log(`[${room.file}] ERROR:`, msg.text());
    });
    page.on('pageerror', err => console.log(`[${room.file}] PAGE ERROR:`, err.message));
    await page.goto(`http://localhost:${port}/${room.file}`);
    await page.waitForTimeout(4000);
    await page.screenshot({ path: path.join(__dirname, room.output) });
    await page.close();
    console.log(`Saved ${room.output}`);
}

await browser.close();
server.close();
