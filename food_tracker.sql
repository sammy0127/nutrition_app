CREATE TABLE log_date (
    id INTEGER PRIMARY KEY autoincrement,
    entry_date DATE not null UNIQUE
);

create table food (
    id INTEGER PRIMARY KEY autoincrement,
    name text not null,
    protein integer not null,
    carbohydrates integer not null,
    fat integer not null,
    calories integer not null
);

create table food_date (
    food_id integer not null,
    log_date_id integer not null,
    primary key(food_id, log_date_id)
);