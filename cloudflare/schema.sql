CREATE TABLE IF NOT EXISTS sensor_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  moisture REAL,
  temp REAL,
  humi REAL,
  created_at DATETIME DEFAULT (datetime('now', 'localtime'))
);
