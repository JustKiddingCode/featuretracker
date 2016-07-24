CREATE TABLE Queue
(
	QueueID INTEGER PRIMARY KEY,
	Name text,
	autoclose boolean
);


CREATE TABLE Queue_NoTicket
(
	QueueID integer REFERENCES Queue(QueueID),
	EMail_Regex text
);

CREATE TABLE Queue_Admin
(
	QueueID integer REFERENCES Queue(QueueID),
	Email_Regex text
);

CREATE TABLE Status
(
	StatusID INTEGER PRIMARY KEY,
	Name text
);


CREATE TABLE Tickets 
(
	TicketID INTEGER PRIMARY KEY,
	Status integer REFERENCES Status(StatusID),
	Owner VARCHAR (254),
	Originator VARCHAR(254),
	Queue integer REFERENCES Queue(QueueID),
	Subject text,
	opened TIMESTAMP WITH TIME ZONE
);


CREATE TABLE Ticket_Dependencies
(
	TicketID REFERENCES Tickets(TicketID),
	depends integer
);

CREATE TABLE EMails
(
	MessageID text PRIMARY KEY,
	Content text
);

CREATE TABLE Link_Ticket_Message 
(
	TicketID REFERENCES Tickets(TicketID),
	MessageID REFERENCES EMails(MessageID)
);



CREATE TABLE Message_to_Queue (
	identifier text,
	value text,
	QueueID references Queue(QueueID)
);

INSERT INTO Status (Name) VALUES 
('Open'), 
('Depending'),
('Closed'),
('Taken');
