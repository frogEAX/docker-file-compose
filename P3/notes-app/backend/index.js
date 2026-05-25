const express = require('express');
const mongoose = require('mongoose');

const app = express();
app.use(express.json());

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, DELETE');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

const Note = mongoose.model('Note', new mongoose.Schema({
  text:      { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
}));

app.get('/notes', async (req, res) => {
  const notes = await Note.find().sort({ createdAt: -1 });
  res.json(notes);
});

app.post('/notes', async (req, res) => {
  const note = await Note.create({ text: req.body.text });
  res.status(201).json(note);
});

app.delete('/notes/:id', async (req, res) => {
  await Note.findByIdAndDelete(req.params.id);
  res.sendStatus(204);
});

const PORT = process.env.PORT || 8080;
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017/notes';

mongoose.connect(MONGO_URL)
  .then(() => app.listen(PORT, () => console.log(`listening on :${PORT}`)))
  .catch(err => { console.error(err); process.exit(1); });
