-- Loco sql export: MySQL inserts
-- Project: Myaamia
-- Locales: en-US, mia
-- Exported by: Michael L.
-- Exported at: Mon, 17 Jun 2024 12:18:10 -0500

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;

/* -- Example schema
 CREATE TABLE `loco_myaamia` (
  `id` VARCHAR(50) NOT NULL COMMENT 'Asset ID', 
  `en_US` BLOB NOT NULL COMMENT 'English (USA)', 
  `mia` BLOB NOT NULL COMMENT 'Miami', 
  PRIMARY KEY  (`id`),
  INDEX `source` (`en_US` (255) )
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
*/

INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Hello','Hello','Aya') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('yes','yes','iihia') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('you\'re welcome','you\'re welcome','iihia') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('affirmative','affirmative','iihia') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('yes','yes','naaka') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('okay','okay','iihia') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('no','no','moohci') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Nobody','Nobody','moohci aweeya') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('No, I cannot','No, I cannot','moohci, niiši neehi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('I said no','I said no','moohci iilwiaani') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Not now','Not now','moohci noonki') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('not','not','moohci') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('welcome','welcome','meentitohkaalilaanki') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('One, 1','One, 1','nkoti') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('two','two','niišwi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Three,','Three,','nihswi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Six','Six','kaakaathswi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Seven','Seven','swaahteethswi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Eight','Eight','palaani') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Ten','Ten','mataathswi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Eleven','Eleven','mataathswi nkotaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twelve, 12','Twelve, 12','mataathswi niišwaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Thirteen, 13','Thirteen, 13','mataathswi nihswaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Fourteen, 14','Fourteen, 14','mataathswi niiwaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Fifteen, 15','Fifteen, 15','mataathswi yaalanwaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Sixteen, 16','Sixteen, 16','mataathswi kaakaathswaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Seventeen, 17','Seventeen, 17','mataathswi swaahteethswaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Eighteen, 18','Eighteen, 18','mataathswi palaanaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('numerals','numerals','akincikoona') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Nineteen','Nineteen','mataathswi nkotimeneehkaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty','Twenty','niišwi mateeni') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty one','Twenty one','niišwi mateeni nkotaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty two,','Twenty two,','niišwi mateeni niišwaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty three, 23','Twenty three, 23','niišwi mateeni nihswaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty four, 24','Twenty four, 24','niišwi mateeni niiwaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty five, 25','Twenty five, 25','niišwi mateeni yaalanwaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty six, 26','Twenty six, 26','niišwi mateeni kaakaathswaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty seven','Twenty seven','niišwi mateeni swaahteethswaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty eight, 28','Twenty eight, 28','niišwi mateeni palaanaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Twenty nine, 29','Twenty nine, 29','niišwi mateeni nkotimeneehkaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Thirty','Thirty','nihswi mateeni') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Thirty five, 35','Thirty five, 35','nihswi mateeni yaalanwaasi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Forty','Forty','niiwi mateeni') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Fifty, 50','Fifty, 50','yaalanwi mateeni') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('One hundred','One hundred','nkotwaahkwe') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Two hundred, 200','Two hundred, 200','niišwaahkwe') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('One thousand, 1000','One thousand, 1000','mataathswaahkwe') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Miami Language’ Online Resources','Miami Language’ Online Resources','Myaamiaataweenki') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Miami','Miami','Myaamia') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('  Myaamia ETHNOBOTANICAL DATABASE','  Myaamia ETHNOBOTANICAL DATABASE','Mahkihkiwa') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Miami Tribe’s revitalization movement','Miami Tribe’s revitalization movement','Myaamiaki Eemamwiciki') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Myaamia Heritage Museum & Archive','Myaamia Heritage Museum & Archive','Kaakisitoonkia') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('corn','corn','Miincipi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('beech tree','beech tree','šeešaakamiš') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('false pennyroyal','false pennyroyal','peecihsakahki') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('hazelnut\n','hazelnut\n','pahkiihteenhsaahkwi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Welcome','Welcome','Aya') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('American hophornbeam','American hophornbeam','myaalwamiši') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Hornbeam','Hornbeam','myaalwamiši') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('sycamore ','sycamore ','kaakhšaahkatw') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('asparagus','asparagus','asparagus') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('Atlantic camas','Atlantic camas','Atlantic camas') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('basswood','basswood','wiikapimiši') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('beet','beet','neehpikiciiphkiki') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('big bluestem grass','big bluestem grass','big bluestem grass') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('black huckleberry','black huckleberry','pinkomini') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('black oak','black oak','maamhkatiaahkatwi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('black walnut tree','black walnut tree','aayoonseekaahkwi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('blue ash','blue ash','sakikansia') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('blueberry','blueberry','pinkomini') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('boneset','boneset','boneset') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('box elder','box elder','šiihšiikweekihsi') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('bull thistle','bull thistle','bull thistle') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('bur oak','bur oak','mihšiinkweemiši') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('butterfly milkweed','butterfly milkweed','alemontehsa') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('butternut tree','butternut tree','kiinošiši') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('cabbage','cabbage','waapinkopakahki') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('calamus root','calamus root','calamus root') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('paper birch ','paper birch ','wiikweehsimiši') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
INSERT INTO `loco_myaamia` (`id`,`en_US`,`mia`) VALUES ('cattail','cattail','apahkwaya') ON DUPLICATE KEY UPDATE `en_US`=VALUES(`en_US`), `mia`=VALUES(`mia`);
 
SET character_set_client = @saved_cs_client;
