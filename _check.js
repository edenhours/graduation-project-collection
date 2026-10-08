const fs = require('fs');
global.window = {};
require('./data.js');
const d = window.ART_DATA;
const ids = new Set();
let bad = [];
d.works.forEach(w => {
  if (ids.has(w.id)) bad.push('DUP ' + w.id);
  ids.add(w.id);
  w.imgs.forEach(i => {
    if (!fs.existsSync('art_thumb/' + i)) bad.push('NO THUMB ' + i + ' (' + w.id + ')');
    if (!fs.existsSync('art_images/' + i)) bad.push('NO RAW ' + i + ' (' + w.id + ')');
  });
});
console.log('total works:', d.works.length);
console.log('problems:', bad.length);
bad.slice(0, 30).forEach(x => console.log(' -', x));
const yrs = {};
d.works.forEach(w => yrs[w.year] = (yrs[w.year] || 0) + 1);
console.log('years:', JSON.stringify(yrs));
console.log('images total:', d.works.reduce((a, w) => a + w.imgs.length, 0));
console.log('files on disk thumb/raw:', fs.readdirSync('art_thumb').length, '/', fs.readdirSync('art_images').length);
