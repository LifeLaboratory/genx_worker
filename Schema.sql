
CREATE TABLE Tasks(
  id SERIAL PRIMARY KEY,
  name text ,
  id_node int  NOT NULL,
  data text,
  status text,
  count_nodes int,
  count_ids text
);

CREATE TABLE TaskResult(
  id SERIAL PRIMARY KEY,
  id_task int,
  id_node int,
  result text
)
