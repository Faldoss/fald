const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);
const fs = require('fs');

const PORT = process.env.PORT || 3000;
const FILE = 'pixels.json';

let pixels = {};
if (fs.existsSync(FILE)) {
  pixels = JSON.parse(fs.readFileSync(FILE, 'utf-8'));
}

app.use(express.static('public'));

io.on('connection', socket => {
  socket.emit('init', pixels);
  socket.on('pixel', data => {
    const key = `${data.x},${data.y}`;
    pixels[key] = data.color;
    fs.writeFileSync(FILE, JSON.stringify(pixels));
    socket.broadcast.emit('pixel', data);
  });
});

http.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
