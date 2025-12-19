-- MySQL dump 10.13  Distrib 9.5.0, for macos26.1 (arm64)
--
-- Host: localhost    Database: parking_db
-- ------------------------------------------------------
-- Server version	9.5.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `campus_events`
--

DROP TABLE IF EXISTS `campus_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `campus_events` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `event_name` varchar(200) DEFAULT NULL,
  `event_type` enum('sports','academic','concert','conference','exam') DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `expected_attendance` int DEFAULT NULL,
  `affected_lots` json DEFAULT NULL,
  `impact_multiplier` decimal(3,2) DEFAULT '1.00',
  PRIMARY KEY (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `campus_events`
--

LOCK TABLES `campus_events` WRITE;
/*!40000 ALTER TABLE `campus_events` DISABLE KEYS */;
/*!40000 ALTER TABLE `campus_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `current_occupancy`
--

DROP TABLE IF EXISTS `current_occupancy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `current_occupancy` (
  `lot_id` int NOT NULL,
  `current_count` int NOT NULL DEFAULT '0',
  `capacity` int NOT NULL,
  `last_updated` datetime NOT NULL,
  `availability_percentage` decimal(5,2) DEFAULT NULL,
  `trend` enum('increasing','decreasing','stable') DEFAULT NULL,
  PRIMARY KEY (`lot_id`),
  CONSTRAINT `current_occupancy_ibfk_1` FOREIGN KEY (`lot_id`) REFERENCES `parking_lots` (`lot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `current_occupancy`
--

LOCK TABLES `current_occupancy` WRITE;
/*!40000 ALTER TABLE `current_occupancy` DISABLE KEYS */;
INSERT INTO `current_occupancy` VALUES (1,0,150,'2025-12-06 18:47:26',100.00,'decreasing'),(2,1,200,'2025-12-06 16:20:19',99.00,'increasing'),(3,2,100,'2025-12-10 18:33:51',99.00,'decreasing'),(4,4,50,'2025-12-06 19:47:46',90.00,'increasing'),(5,0,30,'2025-12-06 13:44:59',100.00,'stable');
/*!40000 ALTER TABLE `current_occupancy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parking_events`
--

DROP TABLE IF EXISTS `parking_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parking_events` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `lot_id` int NOT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `event_type` enum('entry','exit','report') NOT NULL,
  `timestamp` datetime NOT NULL,
  `occupancy_count` int DEFAULT NULL,
  `weather` varchar(50) DEFAULT NULL,
  `temperature` decimal(5,2) DEFAULT NULL,
  `day_of_week` int DEFAULT NULL,
  `is_exam_week` tinyint(1) DEFAULT '0',
  `search_time_minutes` int DEFAULT NULL,
  `registered_user_id` int DEFAULT NULL,
  `spot_number` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_lot_time` (`lot_id`,`timestamp`),
  KEY `registered_user_id` (`registered_user_id`),
  CONSTRAINT `parking_events_ibfk_1` FOREIGN KEY (`lot_id`) REFERENCES `parking_lots` (`lot_id`),
  CONSTRAINT `parking_events_ibfk_2` FOREIGN KEY (`registered_user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parking_events`
--

LOCK TABLES `parking_events` WRITE;
/*!40000 ALTER TABLE `parking_events` DISABLE KEYS */;
INSERT INTO `parking_events` VALUES (1,4,'user_ijuu3wdyo','entry','2025-12-06 16:19:06',NULL,'sunny',70.00,7,0,2,NULL,NULL),(2,4,'user_ijuu3wdyo','exit','2025-12-06 16:19:37',NULL,NULL,NULL,7,0,NULL,NULL,NULL),(3,4,'user_ijuu3wdyo','entry','2025-12-06 16:20:16',NULL,'sunny',70.00,7,0,2,NULL,NULL),(4,2,'user_ijuu3wdyo','entry','2025-12-06 16:20:19',NULL,'sunny',70.00,7,0,2,NULL,NULL),(5,4,'user_1uxd1a4ki','exit','2025-12-06 18:35:37',NULL,NULL,NULL,7,0,NULL,NULL,NULL),(6,1,'user_2smncjt3a','entry','2025-12-06 18:47:10',NULL,'sunny',70.00,7,0,2,NULL,NULL),(7,1,'user_2smncjt3a','exit','2025-12-06 18:47:26',NULL,NULL,NULL,7,0,NULL,NULL,NULL),(8,3,'user_x4cpxtrlf','entry','2025-12-06 19:14:12',NULL,'sunny',70.00,7,0,2,NULL,NULL),(9,4,'user_x4cpxtrlf','entry','2025-12-06 19:29:15',NULL,'sunny',70.00,7,0,2,NULL,NULL),(10,4,'user_x4cpxtrlf','entry','2025-12-06 19:29:21',NULL,'sunny',70.00,7,0,2,NULL,NULL),(11,4,'user_x4cpxtrlf','entry','2025-12-06 19:29:34',NULL,'sunny',70.00,7,0,2,NULL,NULL),(12,4,'user_6lqpyp1d4','entry','2025-12-06 19:47:46',NULL,'sunny',70.00,7,0,2,NULL,NULL),(13,3,'user_6lqpyp1d4','entry','2025-12-06 20:14:19',NULL,'sunny',70.00,7,0,2,NULL,NULL),(14,3,'user_6lqpyp1d4','exit','2025-12-06 20:14:57',NULL,NULL,NULL,7,0,NULL,NULL,NULL),(15,3,'user_6lqpyp1d4','exit','2025-12-06 20:52:32',NULL,NULL,NULL,7,0,NULL,NULL,NULL),(16,3,'user_6lqpyp1d4','exit','2025-12-06 20:52:38',NULL,NULL,NULL,7,0,NULL,NULL,NULL),(17,3,'user_6lqpyp1d4','entry','2025-12-08 00:39:08',NULL,'sunny',70.00,2,0,7,NULL,NULL),(18,3,'user_erhht2mm5','entry','2025-12-08 23:36:38',NULL,'sunny',70.00,2,0,2,NULL,NULL),(19,3,'user_cpvq3t3ck','entry','2025-12-10 18:32:35',NULL,'sunny',70.00,4,0,2,NULL,NULL),(20,3,'user_cpvq3t3ck','exit','2025-12-10 18:32:38',NULL,NULL,NULL,4,0,NULL,NULL,NULL),(21,3,'user_cpvq3t3ck','entry','2025-12-10 18:33:40',NULL,'sunny',70.00,4,0,2,NULL,NULL),(22,3,'user_cpvq3t3ck','exit','2025-12-10 18:33:51',NULL,NULL,NULL,4,0,NULL,NULL,NULL),(23,1,'student@unh.edu','entry','2025-12-10 19:38:31',NULL,'sunny',70.00,2,0,2,5,NULL),(24,1,'student@unh.edu','exit','2025-12-10 19:42:38',NULL,NULL,NULL,2,0,NULL,5,NULL),(25,1,'faculty@unh.edu','entry','2025-12-10 19:56:42',NULL,'sunny',70.00,2,0,2,6,NULL),(26,1,'faculty@unh.edu','entry','2025-12-10 20:04:02',NULL,'sunny',70.00,2,0,2,6,NULL),(27,1,'faculty@unh.edu','entry','2025-12-10 20:08:16',NULL,'sunny',70.00,2,0,2,6,NULL),(28,1,'faculty@unh.edu','entry','2025-12-10 20:08:49',NULL,'sunny',70.00,2,0,2,6,NULL),(29,1,'faculty@unh.edu','exit','2025-12-10 20:08:55',NULL,NULL,NULL,2,0,NULL,6,NULL),(30,1,'student@unh.edu','entry','2025-12-18 17:51:27',NULL,'sunny',70.00,3,0,2,5,'A10'),(31,1,'student@unh.edu','exit','2025-12-18 17:51:30',NULL,NULL,NULL,3,0,NULL,5,'A10'),(32,1,'student@unh.edu','entry','2025-12-18 17:51:38',NULL,'sunny',70.00,3,0,2,5,'A6'),(33,2,'student@unh.edu','entry','2025-12-18 17:51:43',NULL,'sunny',70.00,3,0,2,5,'B9'),(34,2,'faculty@unh.edu','entry','2025-12-18 18:22:52',NULL,'sunny',70.00,3,0,2,6,'B3'),(35,1,'student@unh.edu','entry','2025-12-18 18:23:43',NULL,'sunny',70.00,3,0,2,5,'A10'),(36,1,'student@unh.edu','exit','2025-12-18 18:24:10',NULL,NULL,NULL,3,0,NULL,5,'A10'),(37,1,'student@unh.edu','exit','2025-12-18 18:24:27',NULL,NULL,NULL,3,0,NULL,5,'A6'),(38,2,'student@unh.edu','entry','2025-12-18 18:24:38',NULL,'sunny',70.00,3,0,2,5,'B4'),(39,1,'student@unh.edu','entry','2025-12-18 18:52:11',NULL,'sunny',70.00,3,0,2,5,'A6'),(40,1,'student@unh.edu','entry','2025-12-18 18:52:25',NULL,'sunny',70.00,3,0,2,5,'B3'),(41,2,'student@unh.edu','entry','2025-12-18 19:09:16',NULL,'sunny',70.00,3,0,2,5,'B5'),(42,2,'student@unh.edu','exit','2025-12-18 19:09:50',NULL,NULL,NULL,3,0,NULL,5,'B5'),(43,3,'student@unh.edu','entry','2025-12-18 19:10:06',NULL,'sunny',70.00,3,0,2,5,'A9'),(44,2,'student@unh.edu','exit','2025-12-18 19:10:20',NULL,NULL,NULL,3,0,NULL,5,'B3'),(45,1,'student@unh.edu','exit','2025-12-18 19:15:29',NULL,NULL,NULL,3,0,NULL,5,'A7'),(46,3,'student@unh.edu','exit','2025-12-18 19:15:37',NULL,NULL,NULL,3,0,NULL,5,'A9'),(47,1,'student@unh.edu','entry','2025-12-18 19:18:00',NULL,'sunny',70.00,3,0,2,5,'A7'),(48,1,'faculty@unh.edu','entry','2025-12-18 19:28:57',NULL,'sunny',70.00,3,0,2,6,'A8'),(49,1,'faculty@unh.edu','entry','2025-12-18 19:56:49',NULL,'sunny',70.00,3,0,2,6,'A13'),(50,1,'student@unh.edu','entry','2025-12-18 20:01:35',NULL,'sunny',70.00,3,0,2,5,'A14'),(51,1,'student@unh.edu','exit','2025-12-18 20:01:39',NULL,NULL,NULL,3,0,NULL,5,'A14'),(52,1,'student@unh.edu','entry','2025-12-18 20:07:06',NULL,'sunny',70.00,3,0,2,5,'B2'),(53,1,'student@unh.edu','exit','2025-12-18 20:07:08',NULL,NULL,NULL,3,0,NULL,5,'B2'),(54,1,'student@unh.edu','entry','2025-12-18 20:12:35',NULL,'sunny',70.00,3,0,2,5,'B4'),(55,1,'student@unh.edu','exit','2025-12-18 20:12:39',NULL,NULL,NULL,3,0,NULL,5,'B4');
/*!40000 ALTER TABLE `parking_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parking_lots`
--

DROP TABLE IF EXISTS `parking_lots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parking_lots` (
  `lot_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `capacity` int NOT NULL,
  `latitude` decimal(10,8) NOT NULL,
  `longitude` decimal(11,8) NOT NULL,
  `building_proximity` varchar(200) DEFAULT NULL,
  `type` enum('student','faculty','visitor','mixed') DEFAULT 'mixed',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`lot_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parking_lots`
--

LOCK TABLES `parking_lots` WRITE;
/*!40000 ALTER TABLE `parking_lots` DISABLE KEYS */;
INSERT INTO `parking_lots` VALUES (1,'Pandora Building Lot',150,42.99562800,-71.45478900,'Pandora Building, Academic Center','mixed','2025-12-06 18:43:57'),(2,'Hanover Street Lot',200,42.99412300,-71.45623400,'Main Campus','student','2025-12-06 18:43:57'),(3,'Commercial Street Lot',100,42.99678900,-71.45234500,'Library, Student Center','mixed','2025-12-06 18:43:57'),(4,'Faculty Lot A',50,42.99523400,-71.45567800,'Administrative Building','faculty','2025-12-06 18:43:57'),(5,'Visitor Parking',30,42.99456700,-71.45345600,'Welcome Center','visitor','2025-12-06 18:43:57');
/*!40000 ALTER TABLE `parking_lots` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parking_spots`
--

DROP TABLE IF EXISTS `parking_spots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parking_spots` (
  `spot_id` int NOT NULL AUTO_INCREMENT,
  `lot_id` int NOT NULL,
  `spot_number` varchar(10) NOT NULL,
  `is_occupied` tinyint(1) DEFAULT '0',
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`spot_id`),
  UNIQUE KEY `unique_spot` (`lot_id`,`spot_number`),
  CONSTRAINT `parking_spots_ibfk_1` FOREIGN KEY (`lot_id`) REFERENCES `parking_lots` (`lot_id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parking_spots`
--

LOCK TABLES `parking_spots` WRITE;
/*!40000 ALTER TABLE `parking_spots` DISABLE KEYS */;
INSERT INTO `parking_spots` VALUES (1,1,'A1',0,'2025-12-07 00:12:41'),(2,1,'A2',0,'2025-12-07 00:12:41'),(3,1,'A3',0,'2025-12-07 00:12:41'),(4,1,'A4',0,'2025-12-07 00:12:41'),(5,1,'A5',0,'2025-12-07 00:12:41'),(6,1,'A6',0,'2025-12-07 00:12:41'),(7,1,'A7',0,'2025-12-07 00:12:41'),(8,1,'A8',0,'2025-12-07 00:12:41'),(9,1,'A9',0,'2025-12-07 00:12:41'),(10,1,'A10',0,'2025-12-07 00:12:41'),(11,1,'B1',0,'2025-12-07 00:12:41'),(12,1,'B2',0,'2025-12-07 00:12:41'),(13,1,'B3',0,'2025-12-07 00:12:41'),(14,1,'B4',0,'2025-12-07 00:12:41'),(15,1,'B5',0,'2025-12-07 00:12:41'),(16,1,'B6',0,'2025-12-07 00:12:41'),(17,1,'B7',0,'2025-12-07 00:12:41'),(18,1,'B8',0,'2025-12-07 00:12:41'),(19,1,'B9',0,'2025-12-07 00:12:41'),(20,1,'B10',0,'2025-12-07 00:12:41'),(21,1,'C1',0,'2025-12-07 00:12:41'),(22,1,'C2',0,'2025-12-07 00:12:41'),(23,1,'C3',0,'2025-12-07 00:12:41'),(24,1,'C4',0,'2025-12-07 00:12:41'),(25,1,'C5',0,'2025-12-07 00:12:41'),(26,1,'C6',0,'2025-12-07 00:12:41'),(27,1,'C7',0,'2025-12-07 00:12:41'),(28,1,'C8',0,'2025-12-07 00:12:41'),(29,1,'C9',0,'2025-12-07 00:12:41'),(30,1,'C10',0,'2025-12-07 00:12:41'),(31,2,'A1',0,'2025-12-07 00:12:41'),(32,2,'A2',0,'2025-12-07 00:12:41'),(33,2,'A3',0,'2025-12-07 00:12:41'),(34,2,'A4',0,'2025-12-07 00:12:41'),(35,2,'A5',0,'2025-12-07 00:12:41'),(36,2,'A6',0,'2025-12-07 00:12:41'),(37,2,'A7',0,'2025-12-07 00:12:41'),(38,2,'A8',0,'2025-12-07 00:12:41'),(39,2,'A9',0,'2025-12-07 00:12:41'),(40,2,'A10',0,'2025-12-07 00:12:41'),(41,2,'B1',0,'2025-12-07 00:12:41'),(42,2,'B2',0,'2025-12-07 00:12:41'),(43,2,'B3',0,'2025-12-07 00:12:41'),(44,2,'B4',0,'2025-12-07 00:12:41'),(45,2,'B5',0,'2025-12-07 00:12:41'),(46,2,'B6',0,'2025-12-07 00:12:41'),(47,2,'B7',0,'2025-12-07 00:12:41'),(48,2,'B8',0,'2025-12-07 00:12:41'),(49,2,'B9',0,'2025-12-07 00:12:41'),(50,2,'B10',0,'2025-12-07 00:12:41'),(51,2,'C1',0,'2025-12-07 00:12:41'),(52,2,'C2',0,'2025-12-07 00:12:41'),(53,2,'C3',0,'2025-12-07 00:12:41'),(54,2,'C4',0,'2025-12-07 00:12:41'),(55,2,'C5',0,'2025-12-07 00:12:41'),(56,2,'C6',0,'2025-12-07 00:12:41'),(57,2,'C7',0,'2025-12-07 00:12:41'),(58,2,'C8',0,'2025-12-07 00:12:41'),(59,2,'C9',0,'2025-12-07 00:12:41'),(60,2,'C10',0,'2025-12-07 00:12:41'),(61,3,'A1',0,'2025-12-07 00:12:41'),(62,3,'A2',0,'2025-12-07 00:12:41'),(63,3,'A3',0,'2025-12-07 00:12:41'),(64,3,'A4',0,'2025-12-07 00:12:41'),(65,3,'A5',0,'2025-12-07 00:12:41'),(66,3,'A6',0,'2025-12-07 00:12:41'),(67,3,'A7',0,'2025-12-07 00:12:41'),(68,3,'A8',0,'2025-12-07 00:12:41'),(69,3,'A9',0,'2025-12-07 00:12:41'),(70,3,'A10',0,'2025-12-07 00:12:41'),(71,3,'B1',0,'2025-12-07 00:12:41'),(72,3,'B2',0,'2025-12-07 00:12:41'),(73,3,'B3',0,'2025-12-07 00:12:41'),(74,3,'B4',0,'2025-12-07 00:12:41'),(75,3,'B5',0,'2025-12-07 00:12:41'),(76,3,'B6',0,'2025-12-07 00:12:41'),(77,3,'B7',0,'2025-12-07 00:12:41'),(78,3,'B8',0,'2025-12-07 00:12:41'),(79,3,'B9',0,'2025-12-07 00:12:41'),(80,3,'B10',0,'2025-12-07 00:12:41'),(81,4,'F1',0,'2025-12-07 00:12:41'),(82,4,'F2',0,'2025-12-07 00:12:41'),(83,4,'F3',0,'2025-12-07 00:12:41'),(84,4,'F4',0,'2025-12-07 00:12:41'),(85,4,'F5',0,'2025-12-07 00:12:41'),(86,4,'F6',0,'2025-12-07 00:12:41'),(87,4,'F7',0,'2025-12-07 00:12:41'),(88,4,'F8',0,'2025-12-07 00:12:41'),(89,4,'F9',0,'2025-12-07 00:12:41'),(90,4,'F10',0,'2025-12-07 00:12:41'),(91,5,'V1',0,'2025-12-07 00:12:41'),(92,5,'V2',0,'2025-12-07 00:12:41'),(93,5,'V3',0,'2025-12-07 00:12:41'),(94,5,'V4',0,'2025-12-07 00:12:41'),(95,5,'V5',0,'2025-12-07 00:12:41'),(96,5,'V6',0,'2025-12-07 00:12:41'),(97,5,'V7',0,'2025-12-07 00:12:41'),(98,5,'V8',0,'2025-12-07 00:12:41'),(99,5,'V9',0,'2025-12-07 00:12:41'),(100,5,'V10',0,'2025-12-07 00:12:41');
/*!40000 ALTER TABLE `parking_spots` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prediction_cache`
--

DROP TABLE IF EXISTS `prediction_cache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prediction_cache` (
  `cache_id` int NOT NULL AUTO_INCREMENT,
  `lot_id` int DEFAULT NULL,
  `prediction_time` datetime DEFAULT NULL,
  `predicted_availability` decimal(5,2) DEFAULT NULL,
  `confidence_score` decimal(5,2) DEFAULT NULL,
  `model_version` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cache_id`),
  KEY `lot_id` (`lot_id`),
  KEY `idx_pred_time` (`prediction_time`),
  CONSTRAINT `prediction_cache_ibfk_1` FOREIGN KEY (`lot_id`) REFERENCES `parking_lots` (`lot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prediction_cache`
--

LOCK TABLES `prediction_cache` WRITE;
/*!40000 ALTER TABLE `prediction_cache` DISABLE KEYS */;
/*!40000 ALTER TABLE `prediction_cache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_reports`
--

DROP TABLE IF EXISTS `user_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_reports` (
  `report_id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) NOT NULL,
  `lot_id` int NOT NULL,
  `found_parking` tinyint(1) DEFAULT NULL,
  `search_time_minutes` int DEFAULT NULL,
  `confidence_rating` int DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  `comments` text,
  PRIMARY KEY (`report_id`),
  KEY `lot_id` (`lot_id`),
  KEY `idx_user_time` (`user_id`,`timestamp`),
  CONSTRAINT `user_reports_ibfk_1` FOREIGN KEY (`lot_id`) REFERENCES `parking_lots` (`lot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_reports`
--

LOCK TABLES `user_reports` WRITE;
/*!40000 ALTER TABLE `user_reports` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `role` enum('user','admin') DEFAULT 'user',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (4,'admin@unh.edu','$2b$12$SM7cr7vLNATWsWx/Ao5fl.VjWFKRQmXfMVTFuWwFJe9USHmyPM3LC','Admin User','admin','2025-12-10 23:44:48','2025-12-19 01:43:07',1),(5,'student@unh.edu','$2b$12$Aya4qU0G3yhBzGpHXeWKZusRSbY7GCAlpsl9FT70tvEdxBGOz4jHW','Test Student','user','2025-12-10 23:44:48','2025-12-19 01:45:37',1),(6,'faculty@unh.edu','$2b$12$1t0CZXnpL32w3zph.gB6f.cGHVchX.XR80xDoqe79QBmmDOwvObGO','Test Faculty','user','2025-12-10 23:44:48','2025-12-19 00:34:32',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-18 22:36:45
