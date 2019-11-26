create table flights_table(
    id              int not null,
    depart          varchar(50),
    destination     varchar(50),
    depart_date     int,
    duration        int,
    number_seats    int,
    primary key(id)
);

INSERT INTO flights_table VALUES (1, 'Bucuresti', 'Timisoara', 2, 2, 50);