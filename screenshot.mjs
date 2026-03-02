import { createRequire } from 'module';
const require = createRequire('/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
import { fileURLToPath } from 'url';
import path from 'path';
import http from 'http';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Simple HTTP server
const server = http.createServer((req, res) => {
    let filePath = path.join(__dirname, req.url === '/' ? 'woonkamer.html' : req.url);
    const ext = path.extname(filePath);
    const types = {
        '.html': 'text/html',
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.png': 'image/png',
    };

    // For the main HTML, rewrite importmap to use local files
    if (req.url === '/') {
        let html = fs.readFileSync(filePath, 'utf-8');
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

    fs.readFile(filePath, (err, data) => {
        if (err) { res.writeHead(404); res.end(); return; }
        res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
        res.end(data);
    });
});
await new Promise(resolve => server.listen(0, resolve));
const port = server.address().port;

const browser = await chromium.launch({
    args: ['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

page.on('console', msg => {
    if (msg.type() === 'error') console.log('CONSOLE ERROR:', msg.text());
});
page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

await page.goto(`http://localhost:${port}/`);
// Wait for Three.js to load and render
await page.waitForTimeout(5000);
await page.screenshot({ path: path.join(__dirname, 'render.png') });
await browser.close();
server.close();
console.log('Screenshot saved to render.png');
