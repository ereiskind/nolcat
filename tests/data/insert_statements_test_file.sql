--
-- Table structure for table `COUNTERData`
--

DROP TABLE IF EXISTS `COUNTERData`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `COUNTERData` (
  `COUNTER_data_ID` int(11) NOT NULL,
  `statistics_source_ID` int(11) NOT NULL,
  `report_type` varchar(5) DEFAULT NULL,
  `resource_name` varchar(2000) DEFAULT NULL,
  `publisher` varchar(225) DEFAULT NULL,
  `publisher_ID` varchar(50) DEFAULT NULL,
  `platform` varchar(75) DEFAULT NULL,
  `authors` varchar(1000) DEFAULT NULL,
  `publication_date` datetime DEFAULT NULL,
  `article_version` varchar(50) DEFAULT NULL,
  `DOI` varchar(75) DEFAULT NULL,
  `proprietary_ID` varchar(100) DEFAULT NULL,
  `ISBN` varchar(20) DEFAULT NULL,
  `print_ISSN` varchar(10) DEFAULT NULL,
  `online_ISSN` varchar(20) DEFAULT NULL,
  `URI` varchar(250) DEFAULT NULL,
  `data_type` varchar(25) DEFAULT NULL,
  `section_type` varchar(25) DEFAULT NULL,
  `YOP` smallint(6) DEFAULT NULL,
  `access_type` varchar(20) DEFAULT NULL,
  `access_method` varchar(10) DEFAULT NULL,
  `parent_title` varchar(2000) DEFAULT NULL,
  `parent_authors` varchar(1000) DEFAULT NULL,
  `parent_publication_date` datetime DEFAULT NULL,
  `parent_article_version` varchar(50) DEFAULT NULL,
  `parent_data_type` varchar(25) DEFAULT NULL,
  `parent_DOI` varchar(75) DEFAULT NULL,
  `parent_proprietary_ID` varchar(100) DEFAULT NULL,
  `parent_ISBN` varchar(20) DEFAULT NULL,
  `parent_print_ISSN` varchar(10) DEFAULT NULL,
  `parent_online_ISSN` varchar(10) DEFAULT NULL,
  `parent_URI` varchar(250) DEFAULT NULL,
  `metric_type` varchar(75) NOT NULL,
  `usage_date` date NOT NULL,
  `usage_count` int(11) NOT NULL,
  `report_creation_date` datetime DEFAULT NULL,
  PRIMARY KEY (`COUNTER_data_ID`),
  KEY `statistics_source_ID` (`statistics_source_ID`),
  CONSTRAINT `COUNTERData_ibfk_1` FOREIGN KEY (`statistics_source_ID`) REFERENCES `statisticsSources` (`statistics_source_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `COUNTERData`
--

LOCK TABLES `COUNTERData` WRITE;
/*!40000 ALTER TABLE `COUNTERData` DISABLE KEYS */;
INSERT INTO `COUNTERData` VALUES (13478, 0, 'PR', NULL, NULL, NULL, 'ProQuest', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Other', NULL, NULL, NULL, 'Regular', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Unique_Item_Investigations', '2020-07-01', 77, NULL);
INSERT INTO `COUNTERData` VALUES (13479, 0, 'IR', 'Where Function Meets Fabulous', 'MSI Information Services', NULL, 'ProQuest', 'LJ', '2019-11-01', NULL, NULL, 'ProQuest:2309469258', NULL, '0363-0277', NULL, NULL, 'Journal', NULL, 2019, 'Controlled', 'Regular', 'Library Journal', NULL, NULL, NULL, 'Journal', NULL, 'ProQuest:40955', NULL, '0363-0277', NULL, NULL, 'Unique_Item_Investigations', '2020-07-01', 3, NULL), (13480, 1, 'TR', 'The Yellow Wallpaper', 'Open Road Media', NULL, 'EBSCOhost', NULL, NULL, NULL, NULL, 'EBSCOhost:KBID:8016659', NULL, NULL, NULL, NULL, 'Book', 'Book', 2016, 'Controlled', 'Regular', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Total_Item_Investigations', '2020-07-01', 3, NULL), (13481, 1, 'TR', 'The Yellow Wallpaper', 'Open Road Media', NULL, 'EBSCOhost', NULL, NULL, NULL, NULL, 'EBSCOhost:KBID:8016659', NULL, NULL, NULL, NULL, 'Book', 'Book', 2016, 'Controlled', 'Regular', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Unique_Item_Investigations', '2020-07-01', 4, NULL), (13482, 2, 'TR', 'Library Journal', 'Library Journals, LLC', NULL, 'Gale', NULL, NULL, NULL, NULL, 'Gale:1273', NULL, '0363-0277', NULL, NULL, 'Journal', 'Article', 1998, 'Controlled', 'Regular', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Unique_Item_Requests', '2020-07-01', 3, NULL), (13483, 3, 'PR', NULL, NULL, NULL, 'Duke University Press', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Book', NULL, NULL, NULL, 'Regular', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Unique_Title_Requests', '2020-07-01', 2, NULL), (13484, 3, 'IR', 'Winners and Losers: Some Paradoxes in Monetary History Resolved and Some Lessons Unlearned', 'Duke University Press', NULL, 'Duke University Press', 'Will E. Mason', '1977-11-01', 'VoR', '10.1215/00182702-9-4-476', 'Silverchair:12922', NULL, NULL, NULL, NULL, 'Article', NULL, 1977, 'Controlled', 'Regular', 'History of Political Economy', NULL, NULL, NULL, 'Journal', NULL, 'Silverchair:1000052', NULL, '0018-2702', '1527-1919', NULL, 'Total_Item_Investigations', '2020-07-01', 6, NULL);
/*!40000 ALTER TABLE `COUNTERData` ENABLE KEYS */;
UNLOCK TABLES;