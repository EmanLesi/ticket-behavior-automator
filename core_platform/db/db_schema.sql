DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS ticket;
DROP TABLE IF EXISTS ticket_action;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS category_allocations;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE ticket (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  category INTEGER,
  status CHAR(30) NOT NULL,
  reporter INTEGER NOT NULL,
  assignee INTEGER,
  priority CHAR(20) NOT NULL,
  desc_detail_test INTEGER,
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

CREATE TABLE category_allocations(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ticket INTEGER NOT NULL,
  most_sim_title INTEGER NOT NULL,
  avg_sim_title INTEGER NOT NULL,
  top_5_title INTEGER NOT NULL,
  pers_in_top_10_title INTEGER NOT NULL,
  most_sim_desc INTEGER NOT NULL,
  avg_desc_sim INTEGER NOT NULL,
  conclusion INTEGER NOT NULL,
  FOREIGN KEY (ticket) REFERENCES ticket(id),
  FOREIGN KEY (most_sim_title) REFERENCES category(id),
  FOREIGN KEY (avg_sim_title) REFERENCES category(id),
  FOREIGN KEY (top_5_title) REFERENCES category(id),
  FOREIGN KEY (pers_in_top_10_title) REFERENCES category(id),
  FOREIGN KEY (most_sim_desc) REFERENCES category(id),
  FOREIGN KEY (avg_desc_sim) REFERENCES category(id),
  FOREIGN KEY (conclusion) REFERENCES category(id)
);
