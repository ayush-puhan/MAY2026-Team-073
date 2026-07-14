const db = JSON.parse(require('fs').readFileSync('E:/SWE Project/Application/frontend/public/db.json'));
const keys = Object.keys(db);
console.log('Total top-level keys:', keys.length);
keys.forEach(k => {
  if (Array.isArray(db[k])) {
    const cols = db[k].length > 0 ? Object.keys(db[k][0]) : [];
    console.log(`  TABLE: ${k} | ${db[k].length} rows | columns: ${cols.join(', ')}`);
  } else {
    console.log(`  OBJECT: ${k} (not a table array)`);
  }
});
