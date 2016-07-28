INSERT INTO Message_to_Queue (identifier, value, QueueID) VALUES ('to', 'mathe-info@fsmi.uni-karlsruhe.de', 3);
INSERT INTO Message_to_Queue (identifier, value, QueueID) VALUES ('to', 'info@fsmi.uni-karlsruhe.de', 2);
INSERT INTO Message_to_Queue (identifier, value, QueueID) VALUES ('to', 'mathe@fsmi.uni-karlsruhe.de', 1);
INSERT INTO Message_to_Queue (identifier, value, QueueID) VALUES ('to', 'intern@fsmi.uni-karlsruhe.de', 3);

INSERT INTO Message_to_Queue (identifier, value, QueueID) VALUES ('to', 'mathe-info@fsmi.uka.de', 3);
INSERT INTO Message_to_Queue (identifier, value, QueueID) VALUES ('to', 'info@fsmi.uka.de', 2);
INSERT INTO Message_to_Queue (identifier, value, QueueID) VALUES ('to', 'mathe@fsmi.uka.de', 1);
INSERT INTO Message_to_Queue (identifier, value, QueueID) VALUES ('to', 'intern@fsmi.uka.de', 3);


INSERT INTO Queue (QueueID, Name, autoclose) VALUES (1, 'Mathe Intern', 1);
INSERT INTO Queue (QueueID, Name, autoclose) VALUES (2, 'Info Intern', 1);
INSERT INTO Queue (QueueID, Name, autoclose) VALUES (3, 'Mathe Info Intern', 1);


INSERT INTO Queue_Admin (QueueID, EMail_Regex) VALUES (1, '.*@fsmi.uni-karlsruhe.de');
INSERT INTO Queue_Admin (QueueID, Email_Regex) VALUES (2, '.*@fsmi.uni-karlsruhe.de');
INSERT INTO Queue_Admin (QueueID, EMail_Regex) VALUES (3, '.*@fsmi.uni-karlsruhe.de');



INSERT INTO Queue_NoTicket (QueueID, EMail_Regex) VALUES (1, '.*@fsmi.uni-karlsruhe.de');
INSERT INTO Queue_NoTicket (QueueID, EMail_Regex) VALUES (2, '.*@fsmi.uni-karlsruhe.de');
INSERT INTO Queue_NoTicket (QueueID, EMail_Regex) VALUES (3, '.*@fsmi.uni-karlsruhe.de');
