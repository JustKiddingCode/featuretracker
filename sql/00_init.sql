
CREATE TABLE Queue
(
	Queue-ID SERIAL PRIMARY KEY,
	Name text,
	auto-close boolean
);


CREATE TABLE Queue_NoTicket
(
	Queue-ID integer REFERENCES Queue(Queue-ID),
	EMail_Regex text
);

CREATE TABLE Queue_Admin
(
	Queue-ID integer REFERENCES Queue(Queue-ID),
	Email_Regex text
);

CREATE TABLE Status
(
	Status-ID SERIAL PRIMARY KEY,
	Name text
);


CREATE TABLE Tickets 
(
	Ticket-ID SERIAL PRIMARY KEY,
	Status integer REFERENCES Status(Status-ID),
	Owner VARCHAR (254),
	Originator VARCHAR(254),
	Queue integer REFERENCES Queue(Queue-ID),
	Subject text,
	opened TIMESTAMP WITH TIME ZONE
);


CREATE TABLE Ticket_Dependencies
(
	Ticket-ID REFERENCES Tickets(Ticket-ID),
	depends integer
);

CREATE TABLE EMails
(
	Message-ID text PRIMARY KEY,
	Content text
);

CREATE TABLE Link_Ticket_Message 
(
	Ticket-ID REFERENCES Tickets(Ticket-ID),
	Message-ID REFERENCES EMails(Message-ID)
);


INSERT INTO Status
(
'Open', 'Depending', 'Closed', 'Taken'
);
