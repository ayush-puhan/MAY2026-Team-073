const fs = require('fs');

try {
  const dbPath = './public/db.json';
  const db = JSON.parse(fs.readFileSync(dbPath, 'utf8'));

  // Keys that should be integers if they represent IDs
  const idKeys = [
    'id', 'user_id', 'department_id', 'university_id', 'program_id',
    'interest_id', 'club_id', 'event_id', 'entity_id'
  ];

  for (const collection in db) {
    if (Array.isArray(db[collection])) {
      db[collection].forEach(obj => {
        idKeys.forEach(idKey => {
          if (typeof obj[idKey] === 'string' && /^\d+$/.test(obj[idKey])) {
            obj[idKey] = parseInt(obj[idKey], 10);
          }
        });
      });
    }
  }

  fs.writeFileSync(dbPath, JSON.stringify(db, null, 2));
  console.log('Successfully fixed numeric string IDs to numbers in db.json!');
} catch (error) {
  console.error('Error fixing db.json:', error);
}
