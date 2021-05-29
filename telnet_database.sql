create table `server`(
	`server_ip_port` varchar(30),
    primary key(`server_ip_port`)
);

create table `client`(
	`client_ip_port` varchar(30),
    `server_ip_port` varchar(30),
    foreign key(`server_ip_port`) references `server`(`server_ip_port`),
    primary key(`client_ip_port`)
);

create table `telnet_history_system`(
	`id` int auto_increment,
	`server_ip_port` varchar(30),
    `client_ip_port` varchar(30),
    `date_time` datetime,
    `command` varchar(50),
    primary key(`id`)
);
