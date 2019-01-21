PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL,
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('55fdad4dd0e4');
CREATE TABLE company (
	id INTEGER NOT NULL,
	rank INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL,
	industries VARCHAR(255) NOT NULL,
	revenue FLOAT NOT NULL,
	fiscal_year INTEGER NOT NULL,
	num_employees INTEGER NOT NULL,
	market_cap FLOAT NOT NULL,
	headquarters VARCHAR(255) NOT NULL,
	rev_per_employee FLOAT,
	PRIMARY KEY (id),
	UNIQUE (rank)
);
INSERT INTO company VALUES(1,1,'Samsung Electronics','Mobile Devices, Semiconductor, Personal Computing, Televisions, Blueray DVD',212.68000000000000682,2013,326000,137.90999999999999658,'Seoul, South Korea',652392.99999999999998);
INSERT INTO company VALUES(2,2,'Apple Inc.','Mobile Devices, Personal Computing, Consumer software',182.78999999999999203,2014,98000,616.59000000000003184,'Cupertino, CA, USA (Silicon Valley)',1865199.9999999999999);
INSERT INTO company VALUES(3,3,'Foxconn','OEM Component Manufacturing',132.06999999999999317,2013,1290000,32.149999999999998578,'New Taipei, Taiwan',102379.99999999999999);
INSERT INTO company VALUES(4,4,'HP','Personal Computing and Servers, Consulting',111.45000000000000284,2014,317500,65.299999999999997156,'Palo Alto, CA, USA (Silicon Valley)',351023.99999999999999);
INSERT INTO company VALUES(5,5,'IBM','Computing services, Mainframes',99.750000000000000003,2013,433362,188.21000000000000795,'Armonk, NY, USA',230177.0);
INSERT INTO company VALUES(6,6,'Amazon.com','Internet Retailer, App Hosting',88.989999999999994887,2014,154100,175.21999999999999886,'Seattle, WA, USA',577482.0);
INSERT INTO company VALUES(7,7,'Microsoft','Business computing',86.829999999999998294,2014,128076,370.31000000000000227,'Redmond, WA, USA',677956.99999999999999);
INSERT INTO company VALUES(8,8,'Sony','Electronic Devices, Personal Computing',72.340000000000003409,2014,146300,17.600000000000001421,'Tokyo, Japan',494463.0);
INSERT INTO company VALUES(9,9,'Panasonic','Electronics Devices & Components',70.829999999999998295,2013,293742,22.699999999999999288,'Osaka, Japan',241130.0);
INSERT INTO company VALUES(10,10,'Google','Internet Advertising, Search Engine, Miscellaneous',59.820000000000000282,2013,53546,396.24000000000000908,'Mountain View, CA, USA (Silicon Valley)',1117169.9999999999999);
INSERT INTO company VALUES(12,12,'Toshiba','Semiconductor, Consumer devices',56.200000000000002843,2013,206087,17.670000000000001705,'Tokyo, Japan',272699.99999999999999);
INSERT INTO company VALUES(13,13,'LG Electronics','Personal Computer, Electronics',54.749999999999999999,2013,38718,17.670000000000001705,'Seoul, South Korea',1414070.0);
INSERT INTO company VALUES(14,14,'Intel','Semiconductor',52.70000000000000284,2013,104700,168.47999999999998977,'Santa Clara, CA, USA (Silicon Valley)',503343.0);
CREATE TABLE country (
	id INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL,
	political_system VARCHAR(255) NOT NULL,
	population FLOAT NOT NULL,
	PRIMARY KEY (id)
);
INSERT INTO country VALUES(1,'USA','Representative Democracy',322.0);
INSERT INTO country VALUES(3,'Canada','Democracy',61.999999999999999998);
INSERT INTO country VALUES(4,'Denmark','Democracy',147.0);
INSERT INTO country VALUES(5,'England','Democracy',55.999999999999999999);
INSERT INTO country VALUES(123,'Mexico','Democracy',150.0);
INSERT INTO country VALUES(124,'Uruguay','Democracy',35.0);
INSERT INTO country VALUES(130,'France','Democracy',64.0);
INSERT INTO country VALUES(131,'Croatia','Democracy',5.0);
INSERT INTO country VALUES(132,'South Korea','Democracy',48.000000000000000001);
INSERT INTO country VALUES(133,'China','Dictatorship',1500.0);
CREATE TABLE user (
	id INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);
INSERT INTO user VALUES(1,'Michael Mitchell','mm@mail.com');
INSERT INTO user VALUES(2,'Robert King','rk@mail.com');
INSERT INTO user VALUES(3,'Laura Callahan','lc@mail.com');
INSERT INTO user VALUES(4,'Leonie Kohler','lk@mail.com');
CREATE TABLE employee (
	id INTEGER NOT NULL,
	first_name VARCHAR(255) NOT NULL,
	last_name VARCHAR(255) NOT NULL,
	date DATE NOT NULL,
	salary NUMERIC(8, 2),
	married BOOLEAN NOT NULL,
	company_id INTEGER,
	country_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(company_id) REFERENCES company (id) ON DELETE SET NULL ON UPDATE CASCADE,
	FOREIGN KEY(country_id) REFERENCES country (id) ON DELETE SET NULL ON UPDATE CASCADE,
	CHECK (married IN (0, 1))
);
INSERT INTO employee VALUES(1,'Andrew','Adams','2019-01-18',150,1,1,132);
INSERT INTO employee VALUES(2,'Nancy','Edwards','2019-01-18',100,1,2,1);
INSERT INTO employee VALUES(3,'Jane','Peacock','2019-01-18',68,1,3,133);
INSERT INTO employee VALUES(4,'Margaret','Park','2019-01-18',210,0,1,1);
INSERT INTO employee VALUES(5,'Steve','Johnson','2019-01-18',78,0,1,1);
INSERT INTO employee VALUES(6,'Fernando','Ramos','2019-01-18',345,1,10,123);
CREATE TABLE post (
	id INTEGER NOT NULL,
	body TEXT,
	date DATE NOT NULL,
	user_id INTEGER,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO post VALUES(1,'mm''s first post','2019-01-18',1,'2019-01-18 20:27:15');
INSERT INTO post VALUES(2,'mm''s second post','2019-01-18',1,'2019-01-18 20:27:28');
INSERT INTO post VALUES(3,'rk''s first post','2019-01-18',2,'2019-01-18 20:27:48');
INSERT INTO post VALUES(4,'rk''s 2nd post','2019-01-18',2,'2019-01-18 20:28:07');
COMMIT;
