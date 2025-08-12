/*
 Navicat Premium Data Transfer

 Source Server         : MYSQL
 Source Server Type    : MySQL
 Source Server Version : 80022
 Source Host           : localhost:3306
 Source Schema         : rent_system

 Target Server Type    : MySQL
 Target Server Version : 80022
 File Encoding         : 65001

 Date: 12/08/2025 20:28:39
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admin
-- ----------------------------
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `admin_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `last_login` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of admin
-- ----------------------------
INSERT INTO `admin` VALUES (1, 'lele', 'scrypt:32768:8:1$Sh7fpO5g0usdveeN$73fb14f3004958bfc85641af7fe6ea2de97f335cd1d0a1a12a1b3a6c3bedd04973f4ba48b98c1de2516ce8ca32288a61cc9cfb1567d9466286e01bfef4c61492', '2025-08-09 11:37:59');
INSERT INTO `admin` VALUES (2, 'admin', 'scrypt:32768:8:1$qMPOCdL2hjKHfcbW$f3a306956f807dd7887ac4609d2aec3c71eca58d9f86e6f95a57e38b7ed70df7b5af9f3a766a5602138cda8f72d18cbf768fb61e755e00b4987a64d3f26018e4', '2025-08-12 20:16:48');
INSERT INTO `admin` VALUES (3, 'ling', 'scrypt:32768:8:1$s1UcREb40Colw6li$9b9335bbe8b8c7390c92a9944fb72be176e57e6995744f78530067071423986c37683933b1715bda4fa17d6d7cc2469f679a71022ee128742a6e043d71a45e54', NULL);
INSERT INTO `admin` VALUES (4, 'test', '123456', '2025-08-11 05:13:20');

-- ----------------------------
-- Table structure for app_settings
-- ----------------------------
DROP TABLE IF EXISTS `app_settings`;
CREATE TABLE `app_settings`  (
  `id` int NOT NULL,
  `play_mode` int NULL DEFAULT 0,
  `volume` int NULL DEFAULT 50,
  `theme_mode` int NULL DEFAULT 0,
  `auto_play` tinyint(1) NULL DEFAULT 1,
  `show_lyric` tinyint(1) NULL DEFAULT 1,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of app_settings
-- ----------------------------

-- ----------------------------
-- Table structure for contacts_new
-- ----------------------------
DROP TABLE IF EXISTS `contacts_new`;
CREATE TABLE `contacts_new`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `roomId` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `id_card` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `id_card`(`id_card`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 17 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of contacts_new
-- ----------------------------
INSERT INTO `contacts_new` VALUES (1, '张三', 'A101', '13800138001', '110101199001011234', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (2, '李四', 'B205', '13900139002', '110102199102022345', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (3, '王五', 'C307', '13700137003', '110105199203033456', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (4, '赵六', 'D412', '13600136004', '110106199304044567', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (5, '钱七', 'E518', '13500135005', '110107199405055678', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (6, '孙八', 'F623', '13400134006', '110108199506066789', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (7, '周九', 'G734', '13300133007', '110109199607077890', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (8, '吴十', 'H846', '13200132008', '110110199708088901', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (9, '郑十一', 'I959', '13100131009', '110111199809099012', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (10, '王十二', 'J107', '13000130010', '110112199910101123', '2025-08-03 12:09:10');
INSERT INTO `contacts_new` VALUES (11, '乐乐', 'C501', '18124991801', '440303200408866589', '2025-08-03 04:16:15');
INSERT INTO `contacts_new` VALUES (12, '喷语言', 'C501', '18124991802', '440303200408866580', '2025-08-03 04:18:54');
INSERT INTO `contacts_new` VALUES (17, '吴彦祖', '202', '13800138005', '440303200408866582', '2025-08-03 04:57:15');

-- ----------------------------
-- Table structure for contacts_old
-- ----------------------------
DROP TABLE IF EXISTS `contacts_old`;
CREATE TABLE `contacts_old`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `roomId` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `id_card` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `id_card`(`id_card`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 23 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of contacts_old
-- ----------------------------
INSERT INTO `contacts_old` VALUES (3, '王五', '503', '13800138003', '110101199003033456', '2024-01-17 09:15:00');
INSERT INTO `contacts_old` VALUES (4, '赵六', '504', '13800138004', '110101199004044567', '2024-01-18 16:45:00');
INSERT INTO `contacts_old` VALUES (5, '钱七', '505', '13800138005', '110101199005055678', '2024-01-19 11:30:00');
INSERT INTO `contacts_old` VALUES (6, '孙八', '506', '13800138006', '110101199006066789', '2024-01-20 13:25:00');
INSERT INTO `contacts_old` VALUES (9, '乐乐', 'C501', '18822836193', '440303200408866589', '2025-07-30 14:33:15');
INSERT INTO `contacts_old` VALUES (15, '张三', 'C501', '18124991801', '440303200408866580', '2025-08-03 04:17:24');
INSERT INTO `contacts_old` VALUES (16, '吴彦祖', '202', '13800138000', '440303200408866582', '2025-08-03 04:59:52');
INSERT INTO `contacts_old` VALUES (19, '老刘', '203', '13590186781', '440303200408866578', '2025-08-03 05:01:53');
INSERT INTO `contacts_old` VALUES (20, '老六', '203', '13590186787', '440303200408866579', '2025-08-03 05:02:14');
INSERT INTO `contacts_old` VALUES (21, '钢塑', '101', '13590186767', '440303200408866512', '2025-08-03 05:02:45');
INSERT INTO `contacts_old` VALUES (22, '很积极', '104', '13590186733', '440303200408866521', '2025-08-03 05:03:04');

-- ----------------------------
-- Table structure for contracts_new
-- ----------------------------
DROP TABLE IF EXISTS `contracts_new`;
CREATE TABLE `contracts_new`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `contract_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '合同编号',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `tenant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客姓名',
  `tenant_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客电话',
  `tenant_id_card` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客身份证号',
  `landlord_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '房东' COMMENT '房东姓名',
  `landlord_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '房东电话',
  `monthly_rent` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '月租金',
  `deposit` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '押金',
  `contract_start_date` date NOT NULL COMMENT '合同开始日期',
  `contract_end_date` date NOT NULL COMMENT '合同结束日期',
  `contract_duration` int NOT NULL COMMENT '合同期限(月)',
  `payment_method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '月付' COMMENT '付款方式：月付、季付、半年付、年付',
  `rent_due_date` int NOT NULL DEFAULT 1 COMMENT '每月租金到期日(1-31号)',
  `contract_status` tinyint NOT NULL DEFAULT 1 COMMENT '合同状态：1=生效中, 2=已到期, 3=提前终止, 4=续签',
  `utilities_included` tinyint NOT NULL DEFAULT 0 COMMENT '是否包含水电费：0=不包含, 1=包含',
  `water_rate` decimal(6, 2) NULL DEFAULT 3.50 COMMENT '水费单价(元/吨)',
  `electricity_rate` decimal(6, 2) NULL DEFAULT 0.60 COMMENT '电费单价(元/度)',
  `contract_terms` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '合同条款',
  `special_agreement` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '特殊约定',
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '备注',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_contract_number`(`contract_number`) USING BTREE,
  INDEX `idx_room_number`(`room_number`) USING BTREE,
  INDEX `idx_tenant_name`(`tenant_name`) USING BTREE,
  INDEX `idx_tenant_id_card`(`tenant_id_card`) USING BTREE,
  INDEX `idx_contract_status`(`contract_status`) USING BTREE,
  INDEX `idx_contract_dates`(`contract_start_date`, `contract_end_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '租赁合同表（新）' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of contracts_new
-- ----------------------------
INSERT INTO `contracts_new` VALUES (1, 'HT2024001', 'A101', '张三', '13800138001', '110101199001011234', '王房东', '13900139001', 1500.00, 2000.00, '2024-01-01', '2024-12-31', 12, '月付', 1, 1, 0, 3.50, 0.60, '标准租赁合同，租客需爱护房屋设施', '押一付一', '一年期租赁合同', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `contracts_new` VALUES (2, 'HT2024002', 'A102', '李四', '13800138002', '110101199002021234', '王房东', '13900139001', 1500.00, 2000.00, '2024-02-01', '2025-01-31', 12, '月付', 1, 1, 0, 3.50, 0.60, '标准租赁合同，租客需爱护房屋设施', '押一付一', '需要补交水电费', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `contracts_new` VALUES (3, 'HT2024003', 'B201', '王五', '13800138003', '110101199003031234', '王房东', '13900139001', 1800.00, 2500.00, '2024-01-15', '2024-07-14', 6, '月付', 15, 2, 0, 3.50, 0.60, '标准租赁合同，租客需爱护房屋设施', '押一付一', '半年期租赁合同', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `contracts_new` VALUES (4, 'HT2023004', 'B202', '赵六', '13800138004', '110101199004041234', '王房东', '13900139001', 1800.00, 2500.00, '2023-12-01', '2024-05-31', 6, '月付', 1, 3, 0, 3.50, 0.60, '标准租赁合同，租客需爱护房屋设施', '押一付一', '已退房，押金已退还', '2025-07-29 12:00:00', '2025-07-29 12:00:00');

-- ----------------------------
-- Table structure for contracts_old
-- ----------------------------
DROP TABLE IF EXISTS `contracts_old`;
CREATE TABLE `contracts_old`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `contract_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '合同编号',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `tenant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客姓名',
  `tenant_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客电话',
  `tenant_id_card` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客身份证号',
  `landlord_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '房东' COMMENT '房东姓名',
  `landlord_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '房东电话',
  `monthly_rent` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '月租金',
  `deposit` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '押金',
  `contract_start_date` date NOT NULL COMMENT '合同开始日期',
  `contract_end_date` date NOT NULL COMMENT '合同结束日期',
  `contract_duration` int NOT NULL COMMENT '合同期限(月)',
  `payment_method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '月付' COMMENT '付款方式：月付、季付、半年付、年付',
  `rent_due_date` int NOT NULL DEFAULT 1 COMMENT '每月租金到期日(1-31号)',
  `contract_status` tinyint NOT NULL DEFAULT 1 COMMENT '合同状态：1=生效中, 2=已到期, 3=提前终止, 4=续签',
  `utilities_included` tinyint NOT NULL DEFAULT 0 COMMENT '是否包含水电费：0=不包含, 1=包含',
  `water_rate` decimal(6, 2) NULL DEFAULT 3.50 COMMENT '水费单价(元/吨)',
  `electricity_rate` decimal(6, 2) NULL DEFAULT 0.60 COMMENT '电费单价(元/度)',
  `contract_terms` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '合同条款',
  `special_agreement` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '特殊约定',
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '备注',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_contract_number`(`contract_number`) USING BTREE,
  INDEX `idx_room_number`(`room_number`) USING BTREE,
  INDEX `idx_tenant_name`(`tenant_name`) USING BTREE,
  INDEX `idx_tenant_id_card`(`tenant_id_card`) USING BTREE,
  INDEX `idx_contract_status`(`contract_status`) USING BTREE,
  INDEX `idx_contract_dates`(`contract_start_date`, `contract_end_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '租赁合同表（旧）' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of contracts_old
-- ----------------------------
INSERT INTO `contracts_old` VALUES (1, 'HT2024001', 'A101', '张三', '13800138001', '110101199001011234', '王房东', '13900139001', 1500.00, 2000.00, '2024-01-01', '2024-12-31', 12, '月付', 1, 1, 0, 3.50, 0.60, '标准租赁合同，租客需爱护房屋设施', '押一付一', '一年期租赁合同', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `contracts_old` VALUES (2, 'HT2024002', 'A102', '李四', '13800138002', '110101199002021234', '王房东', '13900139001', 1500.00, 2000.00, '2024-02-01', '2025-01-31', 12, '月付', 1, 1, 0, 3.50, 0.60, '标准租赁合同，租客需爱护房屋设施', '押一付一', '需要补交水电费', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `contracts_old` VALUES (3, 'HT2024003', 'B201', '王五', '13800138003', '110101199003031234', '王房东', '13900139001', 1800.00, 2500.00, '2024-01-15', '2024-07-14', 6, '月付', 15, 2, 0, 3.50, 0.60, '标准租赁合同，租客需爱护房屋设施', '押一付一', '半年期租赁合同', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `contracts_old` VALUES (4, 'HT2023004', 'B202', '赵六', '13800138004', '110101199004041234', '王房东', '13900139001', 1800.00, 2500.00, '2023-12-01', '2024-05-31', 6, '月付', 1, 3, 0, 3.50, 0.60, '标准租赁合同，租客需爱护房屋设施', '押一付一', '已退房，押金已退还', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `contracts_old` VALUES (5, 'HT20250807777', 'B205', '刘七', '13800138005', '', '房东', '', 1600.00, 1800.00, '2024-03-01', '2025-03-01', 12, 'monthly', 1, 1, 0, 3.50, 0.60, '', '', '', '2025-08-07 00:00:00', '2025-08-07 22:43:15');

-- ----------------------------
-- Table structure for rental_info_new
-- ----------------------------
DROP TABLE IF EXISTS `rental_info_new`;
CREATE TABLE `rental_info_new`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `tenant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客姓名',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '联系电话',
  `deposit` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '押金',
  `occupant_count` int NOT NULL DEFAULT 1 COMMENT '入住人数',
  `check_in_date` date NOT NULL COMMENT '入住时间',
  `rental_status` tinyint NOT NULL DEFAULT 1 COMMENT '租住状态：1=正常入住, 2=已退房',
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '备注信息',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_room_number`(`room_number`) USING BTREE,
  INDEX `idx_tenant_name`(`tenant_name`) USING BTREE,
  INDEX `idx_phone`(`phone`) USING BTREE,
  INDEX `idx_check_in_date`(`check_in_date`) USING BTREE,
  INDEX `idx_rental_status`(`rental_status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '租房信息表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of rental_info_new
-- ----------------------------
INSERT INTO `rental_info_new` VALUES (1, 'A101', '张三', '13800138001', 2000.00, 1, '2024-01-01', 1, '一年期租赁合同，单人入住', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `rental_info_new` VALUES (2, 'A102', '李四', '13800138002', 2000.00, 1, '2024-02-01', 1, '需要补交水电费，单人入住', '2025-07-29 12:00:00', '2025-08-05 17:57:42');
INSERT INTO `rental_info_new` VALUES (3, 'A103', '周九', '13800138007', 2000.00, 2, '2024-05-01', 1, '情侣入住，两人', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `rental_info_new` VALUES (4, 'A104', '吴十', '13800138008', 2000.00, 1, '2024-06-01', 1, '学生租客，单人入住', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `rental_info_new` VALUES (5, '909', '爪巴', '18124991809', 200.00, 1, '2025-08-05', 1, '', '2025-08-05 10:49:54', '2025-08-05 10:49:54');
INSERT INTO `rental_info_new` VALUES (6, '908', '乐乐', '18124991878', 200.00, 1, '2025-08-05', 1, '', '2025-08-05 10:52:08', '2025-08-05 10:52:08');
INSERT INTO `rental_info_new` VALUES (7, '506', '下冰雹', '13590185679', 200.00, 1, '2025-08-05', 1, '', '2025-08-05 13:20:11', '2025-08-05 13:20:11');
INSERT INTO `rental_info_new` VALUES (8, '401', 'bosh', '13590185610', 200.00, 1, '2025-08-05', 2, '', '2025-08-09 07:01:59', '2025-08-09 07:01:59');

-- ----------------------------
-- Table structure for rental_info_old
-- ----------------------------
DROP TABLE IF EXISTS `rental_info_old`;
CREATE TABLE `rental_info_old`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `tenant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客姓名',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '联系电话',
  `deposit` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '押金',
  `occupant_count` int NOT NULL DEFAULT 1 COMMENT '入住人数',
  `check_in_date` date NOT NULL COMMENT '入住时间',
  `rental_status` tinyint NOT NULL DEFAULT 1 COMMENT '租住状态：1=正常入住, 2=已退房',
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '备注信息',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_room_number`(`room_number`) USING BTREE,
  INDEX `idx_tenant_name`(`tenant_name`) USING BTREE,
  INDEX `idx_phone`(`phone`) USING BTREE,
  INDEX `idx_check_in_date`(`check_in_date`) USING BTREE,
  INDEX `idx_rental_status`(`rental_status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '租房信息表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of rental_info_old
-- ----------------------------
INSERT INTO `rental_info_old` VALUES (1, 'B201', '王五', '13800138003', 2500.00, 1, '2024-01-15', 1, '半年期租赁合同，入住人数1人', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `rental_info_old` VALUES (2, 'B202', '赵六', '13800138004', 2500.00, 1, '2023-12-01', 2, '已退房，押金已退还', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `rental_info_old` VALUES (3, 'B205', '刘七', '13800138005', 1800.00, 2, '2024-03-01', 1, '夫妻入住，两人', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `rental_info_old` VALUES (4, 'B206', '陈八', '13800138006', 1800.00, 1, '2024-04-01', 1, '单人入住，工作稳定', '2025-07-29 12:00:00', '2025-07-29 12:00:00');
INSERT INTO `rental_info_old` VALUES (5, '505', '乐乐', '18124991878', 200.00, 1, '2025-08-05', 1, '', '2025-08-05 11:34:14', '2025-08-05 11:34:14');
INSERT INTO `rental_info_old` VALUES (6, '506', '流星', '18124991890', 200.00, 2, '2025-08-05', 1, '', '2025-08-05 12:53:50', '2025-08-05 12:53:50');
INSERT INTO `rental_info_old` VALUES (7, '701', '夏雨', '13590185649', 200.00, 1, '2025-08-05', 1, '', '2025-08-05 12:55:48', '2025-08-05 12:55:48');

-- ----------------------------
-- Table structure for rental_new
-- ----------------------------
DROP TABLE IF EXISTS `rental_new`;
CREATE TABLE `rental_new`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `tenant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客姓名',
  `deposit` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '押金',
  `monthly_rent` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '月租金',
  `water_usage` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '用水量(方)',
  `electricity_usage` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '用电量(度)',
  `water_fee` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '水费',
  `electricity_fee` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '电费',
  `utilities_fee` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '水电费',
  `total_due` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '应缴费',
  `payment_status` tinyint NOT NULL DEFAULT 1 COMMENT '租赁状态：1=已缴费, 2=未缴费',
  `check_in_date` date NULL DEFAULT NULL COMMENT '入住时间',
  `check_out_date` date NULL DEFAULT NULL COMMENT '退房时间',
  `contract_start_date` date NULL DEFAULT NULL COMMENT '合同开始时间',
  `contract_end_date` date NULL DEFAULT NULL COMMENT '合同结束时间',
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '备注',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_room_number`(`room_number`) USING BTREE,
  INDEX `idx_tenant_name`(`tenant_name`) USING BTREE,
  INDEX `idx_payment_status`(`payment_status`) USING BTREE,
  INDEX `idx_check_in_date`(`check_in_date`) USING BTREE,
  INDEX `idx_contract_dates`(`contract_start_date`, `contract_end_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '租房管理表（新）' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of rental_new
-- ----------------------------
INSERT INTO `rental_new` VALUES (1, 'A101', '张三', 2000.00, 1500.00, 2.90, 47.70, 80.00, 120.00, 200.00, 1700.00, 1, '2024-01-01', NULL, '2024-01-01', '2024-12-31', '一年期租赁合同', '2025-07-28 22:35:26', '2025-08-09 04:29:25');
INSERT INTO `rental_new` VALUES (2, 'A102', '李四', 2000.00, 1500.00, 7.10, 48.10, 72.00, 108.00, 180.00, 1680.00, 1, '2024-02-01', NULL, '2024-02-01', '2025-01-31', '需要补交水电费', '2025-07-28 22:35:26', '2025-08-09 04:29:25');
INSERT INTO `rental_new` VALUES (3, 'B201', '王五', 2500.00, 1800.00, 3.30, 58.00, 87.85, 132.00, 219.85, 2019.85, 1, NULL, NULL, NULL, NULL, '半年期租赁合同', '2025-07-28 22:35:26', '2025-08-09 04:29:25');
INSERT INTO `rental_new` VALUES (4, 'B202', '赵六', 2500.00, 1800.00, 3.10, 59.80, 0.00, 0.00, 0.00, 1800.00, 1, '2023-12-01', '2024-06-30', '2023-12-01', '2024-05-31', '已退房，押金已退还', '2025-07-28 22:35:26', '2025-08-09 04:29:25');
INSERT INTO `rental_new` VALUES (5, '909', '爪巴', 200.00, 400.00, 0.00, 0.00, 0.00, 0.00, 0.00, 400.00, 2, '2025-08-05', NULL, NULL, NULL, '', '2025-08-09 07:00:27', '2025-08-09 07:00:27');

-- ----------------------------
-- Table structure for rental_old
-- ----------------------------
DROP TABLE IF EXISTS `rental_old`;
CREATE TABLE `rental_old`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `tenant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客姓名',
  `deposit` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '押金',
  `monthly_rent` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '月租金',
  `water_usage` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '用水量(方)',
  `electricity_usage` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '用电量(度)',
  `water_fee` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '水费',
  `electricity_fee` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '电费',
  `utilities_fee` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '水电费',
  `total_due` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '应缴费',
  `payment_status` tinyint NOT NULL DEFAULT 1 COMMENT '租赁状态：1=已缴费, 2=未缴费',
  `check_in_date` date NULL DEFAULT NULL COMMENT '入住时间',
  `check_out_date` date NULL DEFAULT NULL COMMENT '退房时间',
  `contract_start_date` date NULL DEFAULT NULL COMMENT '合同开始时间',
  `contract_end_date` date NULL DEFAULT NULL COMMENT '合同结束时间',
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '备注',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_room_number`(`room_number`) USING BTREE,
  INDEX `idx_tenant_name`(`tenant_name`) USING BTREE,
  INDEX `idx_payment_status`(`payment_status`) USING BTREE,
  INDEX `idx_check_in_date`(`check_in_date`) USING BTREE,
  INDEX `idx_contract_dates`(`contract_start_date`, `contract_end_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '租房管理表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of rental_old
-- ----------------------------
INSERT INTO `rental_old` VALUES (2, 'A102', '李四', 2000.00, 1500.00, 6.00, 24.30, 72.10, 108.00, 180.10, 1680.10, 2, NULL, NULL, NULL, NULL, '需要补交水电费', '2025-07-28 22:35:26', '2025-08-09 04:29:25');
INSERT INTO `rental_old` VALUES (3, 'B201', '王五', 2500.00, 1800.00, 5.90, 24.00, 87.85, 132.00, 219.85, 2019.85, 2, NULL, NULL, NULL, NULL, '半年期租赁合同', '2025-07-28 22:35:26', '2025-08-09 04:29:25');
INSERT INTO `rental_old` VALUES (4, 'B202', '赵六', 2500.00, 1800.00, 3.90, 57.10, 0.00, 0.00, 0.00, 1800.00, 2, NULL, NULL, NULL, NULL, '已退房，押金已退还', '2025-07-28 22:35:26', '2025-08-09 04:29:25');
INSERT INTO `rental_old` VALUES (5, '101', '张三', 0.00, 350.00, 4.60, 53.30, 35.60, 53.40, 89.00, 439.00, 1, '2025-08-02', NULL, NULL, NULL, '', '2025-08-01 12:00:05', '2025-08-09 04:29:25');
INSERT INTO `rental_old` VALUES (10, '701', '夏雨', 200.00, 300.00, 50.00, 30.00, 175.00, 36.00, 211.00, 511.00, 2, NULL, NULL, NULL, NULL, '', '2025-08-09 04:46:57', '2025-08-09 05:06:55');
INSERT INTO `rental_old` VALUES (11, '506', '流星', 200.00, 200.00, 110.00, 90.00, 385.00, 108.00, 493.00, 693.00, 2, NULL, NULL, NULL, NULL, '', '2025-08-09 05:07:26', '2025-08-09 05:07:39');

-- ----------------------------
-- Table structure for rental_records_new
-- ----------------------------
DROP TABLE IF EXISTS `rental_records_new`;
CREATE TABLE `rental_records_new`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `tenant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客姓名',
  `total_rent` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '总租金',
  `payment_date` date NOT NULL COMMENT '缴费时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_room_number`(`room_number`) USING BTREE,
  INDEX `idx_tenant_name`(`tenant_name`) USING BTREE,
  INDEX `idx_payment_date`(`payment_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '租房缴费记录表（新）' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of rental_records_new
-- ----------------------------
INSERT INTO `rental_records_new` VALUES (1, 'A101', '张三', 1700.00, '2024-01-01', '2025-07-29 10:30:00');
INSERT INTO `rental_records_new` VALUES (2, 'B201', '王五', 2020.00, '2024-01-15', '2025-07-29 10:30:00');
INSERT INTO `rental_records_new` VALUES (3, 'A101', '张三', 1700.00, '2024-02-01', '2025-07-29 10:30:00');
INSERT INTO `rental_records_new` VALUES (4, 'A102', '李四', 1680.00, '2025-08-05', '2025-08-05 17:57:42');
INSERT INTO `rental_records_new` VALUES (5, 'B201', '王五', 2019.85, '2025-08-08', '2025-08-08 10:59:10');
INSERT INTO `rental_records_new` VALUES (6, 'TEST_NEW_001', '测试租客_六楼', 1800.00, '2025-08-08', '2025-08-08 11:09:09');
INSERT INTO `rental_records_new` VALUES (7, 'TEST_NEW_001', '测试租客_六楼', 1800.00, '2025-08-08', '2025-08-08 11:09:53');

-- ----------------------------
-- Table structure for rental_records_old
-- ----------------------------
DROP TABLE IF EXISTS `rental_records_old`;
CREATE TABLE `rental_records_old`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `tenant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '租客姓名',
  `total_rent` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '总租金',
  `payment_date` date NOT NULL COMMENT '缴费时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_room_number`(`room_number`) USING BTREE,
  INDEX `idx_tenant_name`(`tenant_name`) USING BTREE,
  INDEX `idx_payment_date`(`payment_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 21 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '租房缴费记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of rental_records_old
-- ----------------------------
INSERT INTO `rental_records_old` VALUES (1, 'A101', '张三', 1700.00, '2024-01-01', '2025-07-29 10:30:00');
INSERT INTO `rental_records_old` VALUES (2, 'B201', '王五', 2020.00, '2024-01-15', '2025-07-29 10:30:00');
INSERT INTO `rental_records_old` VALUES (3, 'A101', '张三', 1700.00, '2024-02-01', '2025-07-29 10:30:00');
INSERT INTO `rental_records_old` VALUES (4, 'A102', '李四', 1680.10, '2025-08-03', '2025-08-03 19:02:46');
INSERT INTO `rental_records_old` VALUES (5, 'B201', '王五', 2019.85, '2025-08-04', '2025-08-04 12:54:15');
INSERT INTO `rental_records_old` VALUES (6, 'A102', '李四', 1680.10, '2025-08-05', '2025-08-05 17:42:29');
INSERT INTO `rental_records_old` VALUES (7, 'A102', '李四', 1680.10, '2025-08-05', '2025-08-05 17:43:01');
INSERT INTO `rental_records_old` VALUES (8, 'B202', '赵六', 1800.00, '2025-08-05', '2025-08-05 17:46:37');
INSERT INTO `rental_records_old` VALUES (9, 'B201', '王五', 2019.85, '2025-08-05', '2025-08-05 17:47:13');
INSERT INTO `rental_records_old` VALUES (10, 'B201', '王五', 2019.85, '2025-08-05', '2025-08-05 17:48:12');
INSERT INTO `rental_records_old` VALUES (11, 'A102', '李四', 1680.10, '2025-08-05', '2025-08-05 17:50:41');
INSERT INTO `rental_records_old` VALUES (12, 'A102', '李四', 1680.10, '2025-08-05', '2025-08-05 17:50:58');
INSERT INTO `rental_records_old` VALUES (13, 'B202', '赵六', 1800.00, '2025-08-05', '2025-08-05 17:51:18');
INSERT INTO `rental_records_old` VALUES (14, 'B201', '王五', 2019.85, '2025-08-05', '2025-08-05 17:52:37');
INSERT INTO `rental_records_old` VALUES (15, 'B201', '王五', 2019.85, '2025-08-05', '2025-08-05 17:53:54');
INSERT INTO `rental_records_old` VALUES (16, '701', '夏雨', 373.00, '2025-08-08', '2025-08-08 11:00:37');
INSERT INTO `rental_records_old` VALUES (17, '506', '流星', 214.10, '2025-08-08', '2025-08-08 11:01:59');
INSERT INTO `rental_records_old` VALUES (18, 'TEST_OLD_001', '测试租客_五楼', 1500.00, '2025-08-08', '2025-08-08 11:09:09');
INSERT INTO `rental_records_old` VALUES (19, 'TEST_OLD_001', '测试租客_五楼', 1500.00, '2025-08-08', '2025-08-08 11:09:53');
INSERT INTO `rental_records_old` VALUES (20, '506', '流星', 214.10, '2025-08-08', '2025-08-08 11:10:12');

-- ----------------------------
-- Table structure for rooms_new
-- ----------------------------
DROP TABLE IF EXISTS `rooms_new`;
CREATE TABLE `rooms_new`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `room_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '单间' COMMENT '房间类型：单间、一室一厅、两室一厅等',
  `deposit` decimal(10, 2) NOT NULL DEFAULT 0.00,
  `base_rent` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '基础租金',
  `room_status` tinyint NOT NULL DEFAULT 1 COMMENT '房间状态：1=空闲, 2=已出租, 3=维修中, 4=停用',
  `water_meter_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '水表编号',
  `electricity_meter_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '电表编号',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_room_number`(`room_number`) USING BTREE,
  INDEX `idx_room_status`(`room_status`) USING BTREE,
  INDEX `idx_room_type`(`room_type`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '房间管理表（新）' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of rooms_new
-- ----------------------------
INSERT INTO `rooms_new` VALUES (1, 'A101', '单间', 200.00, 1500.00, 2, 'SM001', 'EM001', '2025-07-29 12:00:00', '2025-08-05 18:06:43');
INSERT INTO `rooms_new` VALUES (2, 'A102', '单间', 200.00, 1500.00, 2, 'SM002', 'EM002', '2025-07-29 12:00:00', '2025-08-05 18:06:47');
INSERT INTO `rooms_new` VALUES (3, 'A103', '单间', 200.00, 1500.00, 1, 'SM003', 'EM003', '2025-07-29 12:00:00', '2025-08-05 18:06:51');
INSERT INTO `rooms_new` VALUES (4, 'A104', '单间', 200.00, 1500.00, 1, 'SM004', 'EM004', '2025-07-29 12:00:00', '2025-08-05 18:06:55');
INSERT INTO `rooms_new` VALUES (5, 'A105', '单间', 200.00, 1500.00, 1, 'SM005', 'EM005', '2025-07-29 12:00:00', '2025-08-05 18:06:58');
INSERT INTO `rooms_new` VALUES (6, 'A106', '单间', 200.00, 1500.00, 3, 'SM006', 'EM006', '2025-07-29 12:00:00', '2025-08-05 18:07:00');
INSERT INTO `rooms_new` VALUES (7, 'A107', '单间', 200.00, 1500.00, 1, 'SM007', 'EM007', '2025-07-29 12:00:00', '2025-08-05 18:07:02');
INSERT INTO `rooms_new` VALUES (8, 'A108', '单间', 200.00, 1500.00, 1, 'SM008', 'EM008', '2025-07-29 12:00:00', '2025-08-05 18:07:05');
INSERT INTO `rooms_new` VALUES (9, '909', '单间', 200.00, 400.00, 2, 'SM909', 'EM909', '2025-08-05 10:20:39', '2025-08-05 19:49:58');
INSERT INTO `rooms_new` VALUES (10, '908', '单间', 200.00, 300.00, 2, 'SM908', 'EM908', '2025-08-05 10:51:29', '2025-08-05 19:50:06');
INSERT INTO `rooms_new` VALUES (11, '506', '套房', 200.00, 200.00, 2, 'SM506', 'EM506', '2025-08-05 11:50:31', '2025-08-05 21:20:11');
INSERT INTO `rooms_new` VALUES (12, '504', '单间', 200.00, 200.00, 1, 'SM504', 'EM504', '2025-08-05 11:58:02', '2025-08-05 12:50:43');
INSERT INTO `rooms_new` VALUES (13, '401', '单间', 201.00, 500.00, 2, 'SM401', 'EM401', '2025-08-05 12:51:19', '2025-08-09 15:01:59');

-- ----------------------------
-- Table structure for rooms_old
-- ----------------------------
DROP TABLE IF EXISTS `rooms_old`;
CREATE TABLE `rooms_old`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `room_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '房号',
  `room_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '单间' COMMENT '房间类型：单间、一室一厅、两室一厅等',
  `deposit` decimal(10, 2) NOT NULL DEFAULT 0.00,
  `base_rent` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '基础租金',
  `room_status` tinyint NOT NULL DEFAULT 1 COMMENT '房间状态：1=空闲, 2=已出租, 3=维修中, 4=停用',
  `water_meter_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '水表编号',
  `electricity_meter_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '电表编号',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_room_number`(`room_number`) USING BTREE,
  INDEX `idx_room_status`(`room_status`) USING BTREE,
  INDEX `idx_room_type`(`room_type`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '房间管理表（旧）' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of rooms_old
-- ----------------------------
INSERT INTO `rooms_old` VALUES (1, 'B201', '一室一厅', 200.00, 1800.00, 1, 'SM201', 'EM201', '2025-07-29 12:00:00', '2025-08-05 18:06:18');
INSERT INTO `rooms_old` VALUES (2, 'B202', '一室一厅', 200.00, 1800.00, 1, 'SM202', 'EM202', '2025-07-29 12:00:00', '2025-08-05 18:06:20');
INSERT INTO `rooms_old` VALUES (3, 'B203', '一室一厅', 200.00, 1800.00, 1, 'SM203', 'EM203', '2025-07-29 12:00:00', '2025-08-05 18:06:22');
INSERT INTO `rooms_old` VALUES (4, 'B204', '一室一厅', 200.00, 1800.00, 1, 'SM204', 'EM204', '2025-07-29 12:00:00', '2025-08-05 18:06:24');
INSERT INTO `rooms_old` VALUES (5, 'B205', '单间', 200.00, 1600.00, 2, 'SM205', 'EM205', '2025-07-29 12:00:00', '2025-08-05 18:06:27');
INSERT INTO `rooms_old` VALUES (6, 'B206', '单间', 200.00, 1600.00, 1, 'SM206', 'EM206', '2025-07-29 12:00:00', '2025-08-05 18:06:29');
INSERT INTO `rooms_old` VALUES (7, 'B207', '单间', 200.00, 1600.00, 1, 'SM207', 'EM207', '2025-07-29 12:00:00', '2025-08-05 18:06:35');
INSERT INTO `rooms_old` VALUES (9, '505', '单间', 200.00, 400.00, 2, 'SM505', 'EM505', '2025-08-05 11:33:50', '2025-08-05 13:16:32');
INSERT INTO `rooms_old` VALUES (10, '506', '单间', 200.00, 200.00, 2, 'SM506', 'EM506', '2025-08-05 11:44:09', '2025-08-05 13:15:55');
INSERT INTO `rooms_old` VALUES (11, '701', '单间', 200.00, 300.00, 2, 'SM701', 'EM701', '2025-08-05 12:35:47', '2025-08-05 13:15:41');
INSERT INTO `rooms_old` VALUES (12, '201', '两室一厅', 200.00, 600.00, 1, 'SM201', 'EM201', '2025-08-05 13:17:07', '2025-08-05 13:17:07');

SET FOREIGN_KEY_CHECKS = 1;
