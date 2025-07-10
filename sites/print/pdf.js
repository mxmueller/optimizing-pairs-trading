const puppeteer = require('puppeteer');
const fs = require('fs');

async function generateFullSitePDF() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // Liste der URLs, die du exportieren möchtest
  const urls = [
    'http://localhost:1313/docs/'
    // Füge hier deine Seiten hinzu
  ];
  
  let allContent = '';
  
  for (const url of urls) {
    await page.goto(url, { waitUntil: 'networkidle0' });
    
    // Content extrahieren
    const content = await page.evaluate(() => {
      // Navigation und Footer entfernen
      const nav = document.querySelector('nav');
      const footer = document.querySelector('footer');
      if (nav) nav.remove();
      if (footer) footer.remove();
      
      return document.body.innerHTML;
    });
    
    allContent += `<div class="page-break">${content}</div>`;
  }
  
  // Neues HTML mit allem Content
  const fullHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body { font-family: Arial, sans-serif; }
        .page-break { page-break-before: always; }
        .page-break:first-child { page-break-before: auto; }
      </style>
    </head>
    <body>${allContent}</body>
    </html>
  `;
  
  await page.setContent(fullHTML);
  
  await page.pdf({
    path: 'complete-hugo-site.pdf',
    format: 'A4',
    printBackground: true
  });
  
  await browser.close();
  console.log('✅ Vollständige Website als PDF exportiert!');
}

generateFullSitePDF();