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

create table reservations_table(
    res_id           int not null auto_increment,
    flight_id        int not null,
    number_persons   int,
    primary key(res_id),
    foreign key(flight_id) REFERENCES flights_table(id) on delete cascade
);