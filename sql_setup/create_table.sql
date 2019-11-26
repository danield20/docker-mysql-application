create table flights_table(
    id              int not null,
    origin          varchar(50),
    destination     varchar(50),
    depart_date     int,
    depart_hour     int,
    duration        int,
    number_seats    int,
    primary key(id)
);