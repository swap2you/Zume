CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  dept TEXT NOT NULL,
  salary INTEGER NOT NULL
);
INSERT INTO employees (id, name, dept, salary) VALUES
  (1, 'Ada Lovelace', 'QA', 120),
  (2, 'Grace Hopper', 'Engineering', 140),
  (3, 'Alan Turing', 'QA', 110),
  (4, 'Katherine Johnson', 'Data', 130);

CREATE TABLE defects (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL
);
INSERT INTO defects (id, title, severity, status) VALUES
  (1, 'Login timeout', 'high', 'open'),
  (2, 'Typo on homepage', 'low', 'closed'),
  (3, 'Price rounding', 'medium', 'open');
