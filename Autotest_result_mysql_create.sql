CREATE TABLE `operator` (
	`id` int(5) NOT NULL AUTO_INCREMENT,
	`operator` varchar(50) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `dumptemplate` (
	`id` int(3) NOT NULL AUTO_INCREMENT,
	`dumptemplate` varchar(50) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `total` (
	`id` int(6) NOT NULL AUTO_INCREMENT,
	`test` int(3) NOT NULL,
	`operator` int(5) NOT NULL,
	`job` int(3) NOT NULL,
	`build` int(4) NOT NULL,
	`dumptemplate` int(3) NOT NULL,
	`result` varchar(50) NOT NULL,
	`duration` varchar(50) NOT NULL,
	`date` DATETIME NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `test` (
	`id` int(3) NOT NULL AUTO_INCREMENT,
	`test` varchar(50) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `job` (
	`id` int(3) NOT NULL AUTO_INCREMENT,
	`job` varchar(50) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `version` (
	`id` int(5) NOT NULL AUTO_INCREMENT,
	`operator` int(5) NOT NULL,
	`build` int(4) NOT NULL,
	`mass` varchar(50) NOT NULL,
	`ims_s11_sh` varchar(50) NOT NULL,
	`user_registry` varchar(50) NOT NULL,
	`voltegw` varchar(50) NOT NULL,
	`libssrv` varchar(50) NOT NULL,
	PRIMARY KEY (`id`)
);


CREATE TABLE `errors` (
	`id` int(5) NOT NULL AUTO_INCREMENT,
	`operator` int(5) NOT NULL,
	`build` int(4) NOT NULL,
	`test` int(3) NOT NULL,
	`errors` varchar(100) NOT NULL,
	PRIMARY KEY (`id`)
);


ALTER TABLE `total` ADD CONSTRAINT `total_fk0` FOREIGN KEY (`test`) REFERENCES `test`(`id`);

ALTER TABLE `total` ADD CONSTRAINT `total_fk1` FOREIGN KEY (`operator`) REFERENCES `operator`(`id`);

ALTER TABLE `total` ADD CONSTRAINT `total_fk2` FOREIGN KEY (`job`) REFERENCES `job`(`id`);

ALTER TABLE `total` ADD CONSTRAINT `total_fk3` FOREIGN KEY (`dumptemplate`) REFERENCES `dumptemplate`(`id`);

ALTER TABLE `version` ADD CONSTRAINT `version_fk0` FOREIGN KEY (`operator`) REFERENCES `operator`(`id`);

ALTER TABLE `errors` ADD CONSTRAINT `errors_fk0` FOREIGN KEY (`operator`) REFERENCES `operator`(`id`);

ALTER TABLE `errors` ADD CONSTRAINT `errors_fk1` FOREIGN KEY (`test`) REFERENCES `test`(`id`);