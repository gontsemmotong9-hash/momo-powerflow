const express = require('express');
const path = require('path');
require('dotenv').config();

const app = express();

// Enable JSON parsing for incoming requests
app.use(express.json());

// Serve static files (index.html, CSS, JS) from current directory
app.use(express.static(__dirname));

// Default route to explicitly serve index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Import MoMo routes if you have momoRoutes.js
try {
  const momoRoutes = require('./momoRoutes');
  app.use('/api/momo', momoRoutes);
} catch (err) {
  console.log('momoRoutes.js not yet loaded or imported.');
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});