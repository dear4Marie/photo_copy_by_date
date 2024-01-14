CREATE TABLE `photo` (
  `IDX` int(10) NOT NULL,
  `FILE_LOC` varchar(300) DEFAULT NULL,
  `FILE_NAME` varchar(100) DEFAULT NULL,
  `COPY_YN` varchar(1) DEFAULT NULL,
  `COPY_LOC` varchar(300) DEFAULT NULL,
  `FILE_SIZE` bigint(20) DEFAULT NULL,
  `hash` varchar(100) DEFAULT NULL,
  `exif` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `REG_DATE` datetime DEFAULT current_timestamp(),
  `MOD_DATE` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
