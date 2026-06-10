-- DDL Statements for Table Creation
CREATE TABLE cd.members
(
	memid integer NOT NULL,
	surname varchar(200) NOT NULL,
	firstname varchar(200) NOT NULL,
	address varchar(300) NOT NULL,
	zipcode integer NOT NULL,
	telephone varchar(20) NOT NULL,
	recommendedby integer,
	joindata timestamp NOT NULL,
	CONSTRAINT member_pk PRIMARY KEY (memid),
	CONSTRAINT fk_members_recommendedby FOREIGN KEY (recommendedby)
		REFERENCES cd.members(memid) ON DELETE SET NULL
)

CREATE TABLE cd.bookings
(
	bookid integer NOT NULL,
	facid integer NOT NULL,
	memid integer NOT NULL,
	starttime timestamp NOT NULL,
	slots integer NOT NULL,
	CONSTRAINT bookings_pk PRIMARY KEY (bookid),
	CONSTRAINT fk_bookings_facid FOREIGN KEY (facid)
		REFERENCES cd.facilities(facid),
	CONSTRAINT fk_bookings_memid FOREIGN KEY (memid)
		REFERENCES cd.members(memid)
)

CREATE TABLE cd.facilities
(
	facid integer NOT NULL,
	name varchar(100) NOT NULL,
	membercost NUMERIC NOT NULL,
	guestcost NUMERIC NOT NULL,
	initialoutlay NUMERIC NOT NULL,
	monthlymaintenance NUMERIC NOT NULL,
	CONSTRAINT facilities_pk PRIMARY KEY (facid)
)

-- Question 1: https://pgexercises.com/questions/updates/insert.html
INSERT INTO cd.facilities 
VALUES 
  (9, 'Spa', 20, 30, 100000, 800);

-- Question 2: https://pgexercises.com/questions/updates/insert3.html
INSERT INTO cd.facilities (
  facid, name, membercost, guestcost, 
  initialoutlay, monthlymaintenance
) 
VALUES 
  (
    (
      SELECT 
        MAX(facid) 
      FROM 
        cd.facilities + 1
    ), 
    'Spa', 
    20, 
    30, 
    10000, 
    800
  );

-- Question 3: https://pgexercises.com/questions/updates/update.html
UPDATE 
  cd.facilites 
SET 
  initialoutlay = 10000 
WHERE 
  facid = 1;

-- Question 4: https://pgexercises.com/questions/updates/updatecalculated.html
UPDATE 
  cd.facilities 
SET 
  membercost = (
    SELECT 
      membercost * 1.1 
    FROM 
      cd.facilities 
    WHERE 
      facid = 0
  ), 
  guestcost = (
    SELECT 
      guestcost * 1.1 
    FROM 
      cd.facilities 
    WHERE 
      facid = 0
  ) 
WHERE 
  facid = 1;

-- Question 5: https://pgexercises.com/questions/updates/delete.html
DELETE FROM cd.bookings;

-- Question 6: https://pgexercises.com/questions/updates/deletewh.html
DELETE FROM 
  cd.members 
WHERE 
  memid = 37;

-- Question 7: https://pgexercises.com/questions/basic/where2.html
SELECT 
  facid, 
  name, 
  membercost, 
  monthlymaintenance 
FROM 
  cd.facilities 
WHERE 
  membercost > 0 
  AND membercost < monthlymaintenance / 50;

-- Question 8: https://pgexercises.com/questions/basic/where3.html
SELECT 
  * 
FROM 
  cd.facilities 
WHERE 
  name LIKE '%Tennis%';

-- Question 9: https://pgexercises.com/questions/basic/where4.html
SELECT 
  * 
FROM 
  cd.facilities 
WHERE 
  facid IN (1, 5);

-- Question 10: https://pgexercises.com/questions/basic/date.html
SELECT 
  memid, 
  surname, 
  firstname, 
  joindate 
FROM 
  cd.members 
WHERE 
  joindate >= '2012-09-01';

-- Question 11: https://pgexercises.com/questions/basic/union.html
SELECT 
  surname 
FROM 
  cd.members 
UNION 
SELECT 
  name 
FROM 
  cd.facilities;

-- Question 12: https://pgexercises.com/questions/joins/simplejoin.html
SELECT 
  bk.starttime 
FROM 
  cd.bookings bk 
  INNER JOIN cd.members mb ON mb.memid = bk.memid 
WHERE 
  mb.firstname = 'David' 
  AND mb.surname = 'Farrell';

-- Question 13: https://pgexercises.com/questions/joins/simplejoin2.html
SELECT 
  bk.starttime, 
  fc.name 
FROM 
  cd.facilities fc 
  INNER JOIN cd.bookings bk ON bk.facid = fc.facid 
WHERE 
  fc.name LIKE 'Tennis Court%' 
  AND bk.starttime >= '2012-09-21' 
  AND bk.starttime < '2012-09-22' 
ORDER BY 
  bk.starttime;

-- Question 14: https://pgexercises.com/questions/joins/self2.html
SELECT 
  mb.firstname as mbfirstname, 
  mb.surname as mbsurname, 
  rc.firstname as rcfirstname, 
  rc.surname as rcsurname 
FROM 
  cd.members mb 
  LEFT OUTER JOIN cd.members rc ON rc.memid = mb.recommendedby 
ORDER BY 
  mb.surname, 
  mb.firstname;

-- Question 15: https://pgexercises.com/questions/joins/self.html
SELECT 
  DISTINCT mb.firstname, 
  mb.surname 
FROM 
  cd.members mb 
  INNER JOIN cd.members rc ON mb.memid = rc.recommendedby 
ORDER BY 
  mb.surname, 
  mb.firstname;

-- Question 16: https://pgexercises.com/questions/joins/sub.html
SELECT 
  DISTINCT mb.firstname || ' ' || mb.surname as member, 
  (
    SELECT 
      rc.firstname || ' ' || rc.surname as recommendedby 
    FROM 
      cd.members rc 
    WHERE 
      rc.memid = mb.recommendedby
  ) 
FROM 
  cd.members mb 
ORDER BY 
  member;

-- Question 17: https://pgexercises.com/questions/aggregates/count3.html
SELECT 
  recommendedby, 
  count(*) 
FROM 
  cd.members 
WHERE 
  recommendedby IS NOT NULL 
GROUP BY 
  recommendedby 
ORDER BY 
  recommendedby;

-- Question 18: https://pgexercises.com/questions/aggregates/fachours.html
select 
  facid, 
  SUM(slots) as "TotalSlots" 
FROM 
  cd.bookings 
GROUP BY 
  facid 
ORDER BY 
  facid;

-- Question 19: https://pgexercises.com/questions/aggregates/fachoursbymonth.html
SELECT 
  facid, 
  SUM(slots) as "TotalSlotsSept" 
FROM 
  cd.bookings 
WHERE 
  starttime >= '2012-09-01' 
  AND starttime < '2012-10-01' 
GROUP BY 
  facid 
ORDER BY 
  SUM(slots);

-- Question 20: https://pgexercises.com/questions/aggregates/fachoursbymonth2.html
SELECT 
  facid, 
  EXTRACT(
    month 
    FROM 
      starttime
  ) AS month, 
  SUM(slots) AS "TotalSlotsMonth" 
FROM 
  cd.bookings 
WHERE 
  EXTRACT(
    year 
    FROM 
      starttime
  ) = 2012 
GROUP BY 
  facid, 
  month 
ORDER by 
  facid, 
  month;

-- Question 21: https://pgexercises.com/questions/aggregates/members1.html
SELECT 
  COUNT(DISTINCT memid) 
FROM 
  cd.bookings;

-- Question 22: https://pgexercises.com/questions/aggregates/nbooking.html
SELECT 
  mb.surname, 
  mb.firstname, 
  mb.memid, 
  MIN(bk.starttime) 
FROM 
  cd.bookings bk 
  INNER JOIN cd.members mb ON mb.memid = bk.memid 
WHERE 
  starttime >= '2012-09-01' 
GROUP BY 
  mb.surname, 
  mb.firstname, 
  mb.memid 
ORDER by 
  mb.memid;

-- Question 23: https://pgexercises.com/questions/aggregates/countmembers.html
SELECT COUNT(*) OVER(), firstname, surname
FROM cd.members
ORDER BY joindate;

-- Question 24: https://pgexercises.com/questions/aggregates/nummembers.html
SELECT ROW_NUMBER() OVER(ORDER BY joindate), firstname, surname
FROM cd.members
ORDER BY joindate;

-- Question 25: https://pgexercises.com/questions/aggregates/fachours4.html
SELECT 
  facid, 
  total 
FROM 
  (
    SELECT 
      facid, 
      SUM(slots) total, 
      RANK() OVER (
        ORDER BY 
          SUM(slots) DESC
      ) RANK 
    FROM 
      cd.bookings 
    GROUP BY 
      facid
  ) AS ranked 
WHERE 
  RANK = 1;

-- Question 26: https://pgexercises.com/questions/string/concat.html
SELECT 
  surname || ', ' || firstname 
FROM 
  cd.members;

-- Question 27: https://pgexercises.com/questions/string/reg.html
SELECT 
  memid, 
  telephone 
FROM 
  cd.members 
WHERE 
  telephone ~ '[()]';

-- Question 28: https://pgexercises.com/questions/string/substr.html
SELECT 
  SUBSTR(surname, 1, 1) AS letter, 
  COUNT(*) AS count 
FROM 
  cd.members 
GROUP BY 
  letter 
ORDER by 
  letter;

