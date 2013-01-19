/*
Navicat PGSQL Data Transfer

Source Server         : celestia
Source Server Version : 80410
Source Host           : localhost:5432
Source Database       : cah
Source Schema         : public

Target Server Type    : PGSQL
Target Server Version : 80410
File Encoding         : 65001

Date: 2013-01-11 00:58:12
*/


-- ----------------------------
-- Table structure for "public"."cardset"
-- ----------------------------
DROP TABLE "public"."cardset";
CREATE TABLE "public"."cardset" (
"id" serial NOT NULL,
"name" varchar(255) NOT NULL,
"active" bool DEFAULT true NOT NULL,
"base_deck" bool DEFAULT false NOT NULL,
"watermark" varchar(10)
)
WITH (OIDS=FALSE)

;

-- ----------------------------
-- Records of cardset
-- ----------------------------
INSERT INTO "public"."cardset" VALUES ('1', 'First Version', 't', 't', null);
INSERT INTO "public"."cardset" VALUES ('2', 'Second Version', 't', 't', null);
INSERT INTO "public"."cardset" VALUES ('3', 'The First Expansion', 't', 'f', 'X1');
INSERT INTO "public"."cardset" VALUES ('4', 'The Second Expansion', 't', 'f', 'X2');
INSERT INTO "public"."cardset" VALUES ('5', 'Canadian', 'f', 'f', 'CAN');
INSERT INTO "public"."cardset" VALUES ('6', '/r/MLPlounge', 't', 'f', 'MLP');
INSERT INTO "public"."cardset" VALUES ('7', 'BerryTube', 't', 'f', 'BT');
INSERT INTO "public"."cardset" VALUES ('8', '2012 Holiday Pack', 'f', 'f', 'XMAS');
INSERT INTO "public"."cardset" VALUES ('99', 'Marmdrunk', 't', 'f', 'MARM');

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table "public"."cardset"
-- ----------------------------
ALTER TABLE "public"."cardset" ADD PRIMARY KEY ("id");
