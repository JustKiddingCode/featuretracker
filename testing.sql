INSERT INTO Message_to_Queue (identifier, value, QueueID) VALUES ('to', 'notmuch@notmuchmail.org', 1);
INSERT INTO Queue (QueueID, Name, autoclose) VALUES (1, 'Notmuch', 1);
INSERT INTO Queue_Admin (QueueID) VALUES (1, 'alex.boterolowry@gmail.com');


