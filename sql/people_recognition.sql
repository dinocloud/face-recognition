-- MySQL dump 10.13  Distrib 5.7.16, for Linux (x86_64)
--
-- Host: localhost    Database: `people-recognition`
-- ------------------------------------------------------
-- Server version	5.7.16-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE TABLE tenants (
	id INT NOT NULL AUTO_INCREMENT,
	description varchar(200) NOT NULL,
	valid BIT DEFAULT 1 NOT NULL,
	expiration_date TIMESTAMP NULL,
	token varchar(100) DEFAULT test NOT NULL,
	CONSTRAINT tenants_PK PRIMARY KEY (id)
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;

CREATE TABLE cameras (
	id INT NOT NULL AUTO_INCREMENT,
	description VARCHAR(100) NOT NULL,
	id_tenant INT NOT NULL,
	`source` VARCHAR(200) DEFAULT 'Unknown' NOT NULL,
	detection_area INT DEFAULT 300 NOT NULL,
	max_person_age INT DEFAULT 5 NOT NULL,
	source_user varchar(50) NULL,
	source_password varchar(50) NULL,
	CONSTRAINT cameras_PK PRIMARY KEY (id),
	CONSTRAINT cameras_tenants_FK FOREIGN KEY (id_tenant) REFERENCES people_recognition.tenants(id)
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;

CREATE TABLE people_recognition.movements (
	id INT NOT NULL AUTO_INCREMENT,
	`timestamp` TIMESTAMP NOT NULL,
	id_camera INT NOT NULL,
	`type` varchar(3) NOT NULL,
	CONSTRAINT movements_PK PRIMARY KEY (id),
	CONSTRAINT movements_cameras_FK FOREIGN KEY (id_camera) REFERENCES people_recognition.cameras(id)
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;

CREATE TABLE areas (
	id INT NOT NULL AUTO_INCREMENT,
	description varchar(20) NOT NULL,
	CONSTRAINT areas_PK PRIMARY KEY (id)
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;

INSERT into areas(description) values 'in';
INSERT into areas(description) values 'critical';
INSERT into areas(description) values 'out';

CREATE TABLE points (
	id INT NOT NULL AUTO_INCREMENT,
	num_order INT NOT NULL,
	x_value INT NOT NULL,
	y_value INT NOT NULL,
	id_area INT NOT NULL,
	id_camera INT NOT NULL,
	CONSTRAINT points_PK PRIMARY KEY (id),
	CONSTRAINT points_cameras_FK FOREIGN KEY (id_camera) REFERENCES cameras(id),
	CONSTRAINT points_areas_FK FOREIGN KEY (id_area) REFERENCES areas(id)
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;
