export const greetings = [
  "The beautiful thing about learning is nobody can take it away from you. - B.B. King",
  "Education is the most powerful weapon which you can use to change the world. - Nelson Mandela",
  "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
  "Don't let what you cannot do interfere with what you can do. - John Wooden",
  "You don't have to be great to start, but you have to start to be great. - Zig Ziglar",
  "The expert in anything was once a beginner. - Helen Hayes",
  "I think it's possible for ordinary people to choose to be extraordinary. - Elon Musk",
  "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
  "Believe you can and you're halfway there. - Theodore Roosevelt",
  "The only way to do great work is to love what you do. - Steve Jobs",
  "It always seems impossible until it's done. - Nelson Mandela",
  "Dream big and dare to fail. - Norman Vaughan",
  "You are never too old to set another goal or to dream a new dream. - C.S. Lewis",
  "Action is the foundational key to all success. - Pablo Picasso",
  "Do what you can, with what you have, where you are. - Theodore Roosevelt",
  "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
  "Everything you've ever wanted is on the other side of fear. - George Addair",
  "Quality is not an act, it is a habit. - Aristotle",
  "Well done is better than well said. - Benjamin Franklin",
  "Start where you are. Use what you have. Do what you can. - Arthur Ashe"
];

export const getRandomGreeting = () => {
  const index = Math.floor(Math.random() * greetings.length);
  return greetings[index];
};
