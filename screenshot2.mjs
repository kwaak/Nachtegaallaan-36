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
    const types = {
        '.html': 'text/html',
        '.js': 'application/javascript',
    };

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
        // Change camera to look from inside towards the front window
        html = html.replace(
            /camera\.position\.set\(6, 4, 10\)/,
            'camera.position.set(2, 1.6, 4)'
        );
        html = html.replace(
            /controls\.target\.set\(2, 1\.5, 6\)/,
            'controls.target.set(2, 1.5, 12)'
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

await page.goto(`http://localhost:${port}/`);
await page.waitForTimeout(5000);
await page.screenshot({ path: path.join(__dirname, 'render_voorkant.png') });
await browser.close();
server.close();
console.log('Screenshot saved to render_voorkant.png');
