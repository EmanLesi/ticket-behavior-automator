INSERT INTO "user" ("id","username","password") VALUES (1,'test_user','pbkdf2:sha256:260000$ORUgHO8fe1dBFG3m$9c7bcd07bce569ea4aabc7f7aa1a9b4498547f875779c5f9e103a4df9c4ff3b2'),
 (2,'another_user','pbkdf2:sha256:260000$DmG81YSx4gpatOt1$33eae113a517bc7e43f628d54952d6f5b09364cab88f5299714cd7c870b23205'),
 (3,'a_third_user','pbkdf2:sha256:260000$vOCCOtkqw5nmlLVr$9866082225138bef83b2ceabda1f92f6ff4b93f7a6f4213c864e5fef9eb2a6fa');

INSERT INTO "ticket" ("id","title","description","category","status","reporter","assignee","priority","short_description_flag","creation_time","update_time") VALUES (1,'This is the first of many tickets','',NULL,'new',1,NULL,'none',1,'2022-04-13 00:39:51','2022-04-13 00:39:51'),
 (2,'The second of the tickets','Unlike the one before, this ticket has a description.',3,'solution proposed',1,NULL,'none',1,'2022-04-13 00:41:49','2022-04-13 02:16:24'),
 (3,'Banners and shields are off-center when displayed in item frames.','The shield is slightly to left of center, which may be intentional, since it is held off-center? The banner, on the other hand, is overlapping the top edge of the item frame, even though there is enough room for it to fit completely inside.',2,'under investigation',1,2,'low',0,'2022-04-13 00:46:57','2022-04-13 01:07:17'),
 (4,'Shields Off-Centered In Item Frames','Shields are off-centered in item frames.

Thought it would be centered

It wasn''t

Put shield in item frame.',2,'under investigation',1,2,'low',0,'2022-04-13 00:48:28','2022-04-13 01:10:35'),
 (5,'Scroll broken on mac.','When I try to scroll through the item bar it doesn''t respond as it should. It''s not my mouse because it works on versions under 1.12. I really have problems with this and I hope you guys can fix this issue.

Thanks',1,'assigned',1,3,'medium',0,'2022-04-13 00:50:56','2022-04-13 01:03:23'),
 (6,'Scroll does not work','I have been playing minecraft Java on my mac and there is weird sorta glitch that hasnt been fixed since last 2 years.

On my mac i use L-Shift to sprint and whenever i hold down L-Shift to sprint my mouse scroll stops working. It is the glitch from version 1.8+ cause i never played below 1.8',NULL,'new',1,NULL,'none',0,'2022-04-13 00:51:33','2022-04-13 00:51:33'),
 (7,'Unable to scroll while sneaking on macOS','The problem is simple : since the first 1.13 snapshot it is no longer possible to scroll between items while sneaking.

This problem seem to occur on macOS only.',1,'assigned',1,3,'medium',0,'2022-04-13 00:52:27','2022-04-13 01:04:41'),
 (8,'Skeleton horse, skeleton horse chest, zombie horse, mule, and donkey textures are outdated','The skeleton horse saddle still use the old saddle before 1.14 (Texture Update

The zombie horse chest still used the dr zark pouch instead of the vanilla chest

 and the donkey saddle got brown tint on the texture,same for mule',NULL,'new',1,NULL,'none',0,'2022-04-13 00:54:11','2022-04-13 00:54:11'),
 (9,'saddle texture is wrong on some horses','skeleton horse uses the pre 1.14 saddle and chest

and donkey&mule saddle have some weird coloring errors',NULL,'new',1,NULL,'none',0,'2022-04-13 00:54:45','2022-04-13 00:54:45'),
 (10,'Skeleton horse chest is outdated','It uses an outdated texture',NULL,'new',1,NULL,'none',1,'2022-04-13 00:55:17','2022-04-13 00:55:17');

INSERT INTO "ticket_action" ("id","creation_time","ticket","action_type","action_content","associated_user") VALUES (1,'2022-04-13 01:03:06',5,'CHANGED PRIORITY','medium',1),
 (2,'2022-04-13 01:03:06',5,'CHANGED CATEGORY','Mac Scroll Issue',1),
 (3,'2022-04-13 01:03:06',5,'CHANGED ASSIGNEE','test_user',1),
 (4,'2022-04-13 01:03:23',5,'CHANGED ASSIGNEE','a_third_user',1),
 (5,'2022-04-13 01:04:41',7,'CHANGED PRIORITY','medium',1),
 (6,'2022-04-13 01:04:41',7,'CHANGED CATEGORY','Mac Scroll Issue',1),
 (7,'2022-04-13 01:04:41',7,'CHANGED ASSIGNEE','a_third_user',1),
 (8,'2022-04-13 01:06:43',3,'CHANGED PRIORITY','low',2),
 (9,'2022-04-13 01:06:43',3,'CHANGED CATEGORY','Off Center Items',2),
 (10,'2022-04-13 01:06:43',3,'CHANGED ASSIGNEE','another_user',2),
 (11,'2022-04-13 01:06:52',3,'CHANGED STATUS','under investigation',2),
 (12,'2022-04-13 01:07:17',3,'MADE A COMMENT','We are currently working on a fix for this issue',2),
 (13,'2022-04-13 01:10:35',4,'CHANGED ASSIGNEE','another_user',0),
 (14,'2022-04-13 01:10:35',4,'CHANGED STATUS','under investigation',0),
 (15,'2022-04-13 01:10:35',4,'CHANGED PRIORITY','low',0),
 (16,'2022-04-13 01:10:35',4,'CHANGED CATEGORY','Off Center Items',0),
 (17,'2022-04-13 01:30:24',2,'PROPOSED A SOLUTION','this is a test solution',2),
 (18,'2022-04-13 01:30:24',2,'CHANGED STATUS','solution proposed',2),
 (19,'2022-04-13 02:16:24',2,'CHANGED CATEGORY','Category That Exists',2);

INSERT INTO "category" ("id","name","creation_time") VALUES (1,'Mac Scroll Issue','2022-04-13 01:03:06'),
 (2,'Off Center Items','2022-04-13 01:06:43'),
 (3,'Category That Exists','2022-04-13 02:16:24');

INSERT INTO "ticket_similarity" ("id","creation_time","ticket","comp_ticket","title_sim","desc_sim") VALUES (1,'2022-04-13 00:41:49',2,1,0.9285,0.6823),
 (3,'2022-04-13 00:52:27',7,5,0.7688,0.8814),
 (4,'2022-04-13 00:54:46',9,8,0.769,0.8881),
 (5,'2022-04-13 00:55:17',10,8,0.8453,0.5647),
 (7,'2022-04-13 01:10:35',4,3,0.9141,0.8393),
 (8,'2022-04-13 01:28:59',8,9,0.769,0.8881);