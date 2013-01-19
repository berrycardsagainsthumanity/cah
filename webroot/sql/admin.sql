DROP TABLE "public"."admin";
CREATE TABLE "public"."admin" (
"id" serial NOT NULL,
"password" varchar(255) NOT NULL
)
WITH (OIDS=FALSE)
;
ALTER TABLE "public"."admin" ADD PRIMARY KEY ("id");