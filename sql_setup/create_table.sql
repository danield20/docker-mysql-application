create table flights_table(
    id              int not null,
    origin          varchar(50),
    destination     varchar(50),
    depart_date     int,
    depart_hour     int,
    duration        int,
    capacity        int,
    seats_taken     int,
    primary key(id)
);

create table reservations_table(
    res_id           int not null,
    number_persons   int,
    primary key(res_id)
);

create table reservations_flights(
    res_id          int not null,
    flight_id       int not null,
    foreign key(res_id) REFERENCES reservations_table(res_id) on delete cascade,
    foreign key(flight_id) REFERENCES flights_table(id) on delete cascade
);

create table bought_tickets(
    book_id         int not null auto_increment,
    res_id          int not null,
    card_info       varchar(50),
    primary key (book_id),
    foreign key(res_id) REFERENCES reservations_table(res_id) on delete cascade
);

create table admin_credentials(
    username        varchar(60),
    pass            varchar(60)
);

insert into admin_credentials values ("admin", "sprc2019");
