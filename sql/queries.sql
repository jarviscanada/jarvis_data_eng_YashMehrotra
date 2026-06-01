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