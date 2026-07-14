const fs = require('fs');
const path = require('path');

const dbPath = path.join(__dirname, 'public', 'db.json');

try {
  const data = JSON.parse(fs.readFileSync(dbPath, 'utf8'));
  
  if (data.users && Array.isArray(data.users)) {
    let updated = 0;
    data.users = data.users.map(user => {
      if (user.color_blind_mode === undefined) {
        user.color_blind_mode = false;
        updated++;
      }
      return user;
    });
    
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2), 'utf8');
    console.log(`Successfully added color_blind_mode to ${updated} users.`);
  } else {
    console.log("No users array found in db.json");
  }
} catch (e) {
  console.error("Failed to update db.json:", e);
}
