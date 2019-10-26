CREATE TYPE statuses AS ENUM ('pending', 'scheduled', 'succeded');


CREATE TABLE Tasks(
  id SERIAL PRIMARY KEY,
  nodeId integer  NOT NULL,
  status text,
);

CREATE TABLE TaskResult(
  id SERIAL PRIMARY KEY,
  taskId integer,
  data text
)
