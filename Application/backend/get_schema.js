const fs = require('fs');
const path = require('path');

const modelsDir = 'E:/SWE_Project/Application/backend/app/database/models';
const files = fs.readdirSync(modelsDir).filter(f => f.endsWith('.py'));

files.forEach(f => {
  const c = fs.readFileSync(path.join(modelsDir, f), 'utf8');
  const tableRegex = /__tablename__ = "(.*?)"/g;
  let match;
  while ((match = tableRegex.exec(c)) !== null) {
    console.log('\nTable:', match[1]);
    
    // Simplistic column matching for that block
    // We'll just extract all lines with " = Column(" 
    const lines = c.split('\n');
    let inTable = false;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(`__tablename__ = "${match[1]}"`)) {
        inTable = true;
      }
      else if (inTable && lines[i].includes('class ')) {
        inTable = false; // Next class
      }
      if (inTable && lines[i].includes('= Column(')) {
        const colMatch = lines[i].match(/([a-zA-Z0-9_]+)\s*=\s*Column\(/);
        if (colMatch) {
          console.log('  ', colMatch[1]);
        }
      }
    }
  }
});
