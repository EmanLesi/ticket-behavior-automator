DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS ticket;
DROP TABLE IF EXISTS ticket_action;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS ticket_similarity;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE ticket (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT DEFAULT 'NO DESCRIPTION',
  category INTEGER,
  status CHAR(30) NOT NULL DEFAULT 'new',
  reporter INTEGER NOT NULL,
  assignee INTEGER,
  priority CHAR(20) NOT NULL DEFAULT 'none',
  short_description_flag INTEGER DEFAULT 1,
  creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category) REFERENCES category(id),
  FOREIGN KEY (reporter) REFERENCES user(id),
  FOREIGN KEY (assignee) REFERENCES user(id)
);

CREATE TABLE ticket_action (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ticket INTEGER NOT NULL,
  action_type CHAR(20) NOT NULL,
  action_content TEXT,
  associated_user INTEGER NOT NULL,
  FOREIGN KEY (ticket) REFERENCES ticket(id),
  FOREIGN KEY (associated_user) REFERENCES user(id)
);

CREATE TABLE category(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ticket_similarity(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ticket INTEGER NOT NULL,
  comp_ticket INTEGER NOT NULL,
  title_sim REAL NOT NULL,
  desc_sim REAL NOT NULL,
  FOREIGN KEY (ticket) REFERENCES ticket(id),
  FOREIGN KEY (comp_ticket) REFERENCES ticket(id)
);
