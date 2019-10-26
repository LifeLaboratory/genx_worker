CREATE TYPE statuses AS ENUM ('pending', 'scheduled', 'succeded');


CREATE TABLE Tasks(
  id SERIAL PRIMARY KEY,
  nodeid integer  NOT NULL,
  status text,
);

CREATE TABLE TaskResult(
  id SERIAL PRIMARY KEY,
  taskid integer,
  data text
)
