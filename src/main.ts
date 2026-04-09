import express, { Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import path from 'path';
import fs from 'fs/promises';
import NodeCache from 'node-cache';
import MarkdownIt from 'markdown-it';
import { fileURLToPath } from 'url';
import * as scrapper from './scrapper.js';
import * as weather from './weather.js';
import * as icalGen from './ical_gen.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const markdown = new MarkdownIt();
const cache = new NodeCache({ stdTTL: 3600, checkperiod: 600 });

const DOC_DIR = path.join(__dirname, '..', 'doc');

// Security middleware
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'", 'https:'],
        scriptSrc: ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
        styleSrc: ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
        imgSrc: ["'self'", 'data:'],
      },
    },
    hsts: { maxAge: 31536000, includeSubDomains: true },
  })
);

// CORS
app.use(cors({
  origin: '*',
  methods: ['GET'],
}));

// Static files
app.use('/static', express.static(DOC_DIR));

// Set template engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '..', 'templates'));

// Routes
app.get('/ical', async (req: Request, res: Response) => {
  const weatherEnabled = req.query.weather !== 'false';
  const cacheKey = `ical_${weatherEnabled}`;

  let icalContent = cache.get(cacheKey);

  if (!icalContent) {
    try {
      const events = await scrapper.fetchEvents();

      if (weatherEnabled) {
        const weatherData = await weather.fetchWeather();
        weather.assignWeather(events, weatherData);
      }

      icalContent = icalGen.createIcal(events, weatherEnabled);
      cache.set(cacheKey, icalContent);
    } catch (error) {
      console.error('Error generating iCal:', error);
      res.status(500).send('Error generating calendar');
      return;
    }
  }

  res.setHeader('Content-Type', 'text/calendar');
  res.setHeader('Content-Disposition', 'attachment; filename=vrbne.ics');
  res.send(icalContent);
});

app.get('/', async (req: Request, res: Response) => {
  try {
    let content = '';
    const files = ['readme.md', 'google.md', 'outlook.md'];

    // Get the base URL for static files, considering proxy
    const protocol = req.get('x-forwarded-proto') || req.protocol;
    const host = req.get('x-forwarded-host') || req.get('host') || '';
    
    // Pro vrbne - pokud víme, že běžíme pod /vrbne a proxy nám neposílá X-Forwarded-Prefix, ale posílá Host.
    // Předpokládáme, že root_path by mohl být /vrbne, stejně jako v Python verzi.
    let prefix = req.get('x-forwarded-prefix') || '';
    if (!prefix && req.get('x-forwarded-host')) {
        prefix = '/vrbne';
    }
    
    // Zajistíme, že prefix začíná lomítkem a nekončí jím, pokud to není jen /
    if (prefix && !prefix.startsWith('/')) prefix = '/' + prefix;
    if (prefix.endsWith('/') && prefix !== '/') prefix = prefix.slice(0, -1);

    const staticUrl = `${protocol}://${host}${prefix}/static`.replace(/\/+/g, '/').replace(':/', '://');

    // Get absolute URL for iCal endpoint
    const icalUrl = `${protocol}://${host}${prefix}/ical`.replace(/\/+/g, '/').replace(':/', '://');

    for (const filename of files) {
      const filePath = path.join(DOC_DIR, filename);
      try {
        const mdContent = await fs.readFile(filePath, 'utf-8');

        // Fix paths in markdown for static files
        const fixedContent = mdContent.replace(
          /(!?\[.*?\])\((.*?)\)/g,
          (match, prefix: string, url: string) => {
            // If it's a reference to one of our documentation files, change it to anchor
            if (files.includes(url)) {
              return `${prefix}(#${url})`;
            }

            // If it's absolute or external, keep it
            if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/')) {
              return `${prefix}(${url})`;
            }

            // Otherwise, prepend static URL
            return `${prefix}(${staticUrl}/${url})`;
          }
        );

        const html = markdown.render(fixedContent);
        content += `<section id="${filename}">${html}</section><hr>`;
      } catch (error) {
        console.error(`Error reading file ${filename}:`, error);
      }
    }

    res.render('index', { content, ical_url: icalUrl });
  } catch (error) {
    console.error('Error rendering index:', error);
    res.status(500).send('Error rendering page');
  }
});

app.get('/favicon.ico', (_req: Request, res: Response) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <text y=".9em" font-size="90">🌊</text>
    </svg>
  `;
  res.setHeader('Content-Type', 'image/svg+xml');
  res.send(svg);
});

const PORT = parseInt(process.env.PORT || '8000', 10);
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
