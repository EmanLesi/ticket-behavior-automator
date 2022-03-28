INSERT INTO user (username, password)
VALUES
  ('test_user', 'pbkdf2:sha256:260000$duNuMXAuWSyjc45T$fba76f959af6281fb7a1bd6c1879a1811138db4f3af7a9707cce27033614db93'),
  ('another_user', 'pbkdf2:sha256:260000$tN4G5nhzzAKKZnZL$8ac1b05ac250a6df6a8d2ac78368e58efb738febb90a054d6c93100750e43e2a'),
  ('third_user', 'pbkdf2:sha256:260000$cNsnqdTvE76DXhAu$6778e58aaf1e993e2ef32b84250bbaafaf24d6b85337206fcee54d5cb038594c');

INSERT INTO ticket (title, description, category, status, reporter, assignee, priority, creation_time, update_time)
VALUES
  ("Not able to make ticket Titles","this is a test ticket that is used to show that ticket functions work well on this platform",
  1, "under investigation", 1, 2, "high", datetime(1648308712,'unixepoch'), datetime(1648309046,'unixepoch')),
  ("This is a second ticket", "This ticket has a short description", NULL, "new", 3, NULL, "none",
  datetime(1648101746, 'unixepoch'), datetime(1648101746, 'unixepoch')),
  ("This is a completed ticket", NULL,
  NULL, "solution proposed", 1, 2, "low", datetime(1648098451,'unixepoch'), datetime(1648227068,'unixepoch'));

INSERT INTO category (name, creation_time)
VALUES
  ("initial test category", datetime(1648003391, 'unixepoch')),
  ("secondary test category", datetime(1648049607, 'unixepoch')),
  ("tertiary test category", datetime(1648078111, 'unixepoch'));

INSERT INTO ticket_action (creation_time, ticket, action_type, action_content, associated_user)
VALUES
  (datetime(1648308902,'unixepoch'), 1,"CHANGED ASSIGNEE","another_user", 2),
  (datetime(1648309032,'unixepoch'), 1,"CHANGED STATUS","under investigation", 2),
  (datetime(1648309032,'unixepoch'), 1,"CHANGED CATEGORY","initial test category", 2),
  (datetime(1648309046,'unixepoch'), 1,"CHANGED PRIORITY","high", 2),
  (datetime(1648227000,'unixepoch'), 3,"CHANGED ASSIGNEE","another_user", 2),
  (datetime(1648227010,'unixepoch'), 3,"CHANGED PRIORITY","low", 2),
  (datetime(1648227057,'unixepoch'), 3,"MADE A COMMENT","this is a test ticket", 2),
  (datetime(1648227068,'unixepoch'), 3,"PROPOSED A SOLUTION","this is a proposed solution for test ticket", 2);
