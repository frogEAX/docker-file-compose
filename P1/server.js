import express from 'express';
import sqlite3 from 'sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

const app = express();
const port = 3000;

// Настройка путей
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(express.json());
app.use(express.static(__dirname));

// Подключение к БД (файл todo.db создастся сам)
const db = new sqlite3.Database('/tmp/todo.db', (err) => {
    if (err) console.error(err.message);
    console.log('Подключено к базе данных SQLite в /tmp.');
});

// Создание таблицы, если её нет
db.run(`CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL
)`);

// Главная страница
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Получить все задачи
app.get('/api/todos', (req, res) => {
    db.all('SELECT * FROM todos', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// Добавить задачу
app.post('/api/todos', (req, res) => {
    const { task } = req.body;
    db.run('INSERT INTO todos (task) VALUES (?)', [task], function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ id: this.lastID, task });
    });
});

// Удалить задачу
app.delete('/api/todos/:id', (req, res) => {
    const { id } = req.params;
    db.run('DELETE FROM todos WHERE id = ?', id, function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ deleted: this.changes });
    });
});

app.listen(port, () => {
    console.log(`Сервер запущен на http://localhost:${port}`);
});

