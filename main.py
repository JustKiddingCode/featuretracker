#!/usr/bin/python3

import email as e
from email.mime.text import MIMEText
import sys
import re
import logging
import io


from subprocess import Popen, PIPE

import database
import config


####################################
###          Datatypes etc       ###
####################################

def enum(*args):
	enums = dict(zip(args, range(len(args))))
	return type('Enum', (), enums)

errors = enum('NO_MESSAGE_ID', 'ENCODING','NO_QUEUE', 'ALREADY_PROCESSED_EMAIL')


####################################
### COMMANDS WITH DATABASE ACCESS###
###       AND COMPLETE EMAIL     ###
####################################


def save_message(email):
	query = "INSERT INTO Emails (MessageID, Content) VALUES (?,?)"
	database.cursor.execute(query, (email['message-id'], str(email)))


def search_queue_by_email(email):
	LOGGER.debug("Search queue by email, email_to: %s", email['To'])
	# TO
	query = "SELECT QueueID FROM Message_to_Queue WHERE identifier='to' and value = ?"

	database.cursor.execute(query, (email['To'], ))
	val = database.cursor.fetchone()
	if (val is None):
		return -1
	return val[0]

####################################
### COMMANDS WITH DATABASE ACCESS###
####################################


def list_ticket(status_id, queue_id):
	query = "SELECT Originator, opened, Subject FROM Tickets WHERE Queue = ? AND Status= ?"
	database.cursor.execute(query, (queue_id, status_id))

	ticket_list = ""

	for row in database.cursor.fetchall():
		ticket_list += "%s %s %s \n\n" % (row[0], row[1], row[2])

	return ticket_list


def list_open_tickets(queue_id):
	query = "SELECT StatusID From Status WHERE Name=?"
	database.cursor.execute(query, ("Open",))
	status_id = database.cursor.fetchone()[0]
	email_body = list_ticket(status_id, queue_id)

	return email_body

	
def search_ticket_id_by_references(references):
	query = "Select TicketID FROM Link_Ticket_Message WHERE MessageID in (%s)" \
		% ','.join('?' * len(references))

	database.cursor.execute(query, references)
	val = database.cursor.fetchone()

	if (val is None):
		return -1
	else:
		return val[0]


def check_existence(message_id):
	query = "SELECT Count(*) FROM Emails WHERE MessageID = ?"
	database.cursor.execute(query, (message_id, ))
	count = database.cursor.fetchone()[0]

	if (count > 0):
		LOGGER.debug("E-Mail already in Database. Exit")
		return True
	return False


def link_message_ticket(message_id, ticket_id):
	query = "INSERT INTO Link_Ticket_Message (TicketID, MessageID) VALUES (?,?)"
	database.cursor.execute(query, (ticket_id, message_id))

def create_ticket(originator, queue_id, subject):
	LOGGER.debug("Create ticket %s, %s %s ", originator, queue_id, subject)

	# Get open status id
	query = "SELECT StatusID FROM Status WHERE Name = 'Open'"
	database.cursor.execute(query)
	val = database.cursor.fetchone()
	if (val is None):
		LOGGER.debug("Could not determine status id for Status Open. Exit.")
		return

	status_id = val[0]

	query = ("INSERT INTO Tickets (Status, Originator, Queue, Subject, opened) "
		"VALUES (?,?,?,?, datetime('now'))")
	database.cursor.execute(query, (status_id, originator, queue_id, subject))

	#TODO: none sqlite way
	query = "SELECT last_insert_rowid()"
	database.cursor.execute(query)

	return database.cursor.fetchone()[0]

def get_queue_id_from_ticket_id(ticket_id):
	query = "SELECT Queue FROM Tickets WHERE TicketID = ?"
	database.cursor.execute(query, (ticket_id, ))
	queue_id = database.cursor.fetchone()[0]

	return queue_id



def check_admin(from_email, queue_id):
	LOGGER.debug("Check Admin %s ", from_email)
	query = "SELECT Email_Regex FROM Queue_Admin WHERE QueueID = ?"
	database.cursor.execute(query, (queue_id, ))

	LOGGER.debug("Testing for mail adress %s", from_email)
	for line in database.cursor.fetchall():
		regex = line[0]
		LOGGER.debug("Found regex: %s", regex)
		if (re.match(regex, from_email)):
			return True

	return False

def check_autoclose(queue_id):
	query = "SELECT autoclose FROM Queue WHERE QueueID = ?"
	database.cursor.execute(query, (queue_id, ))

	val = database.cursor.fetchone()
	return (val[0] == 1)


def check_noticket(from_mail, queue_id):

	query = "SELECT Email_Regex FROM Queue_NoTicket WHERE QueueID = ?"
	database.cursor.execute(query, (queue_id, ))

	LOGGER.debug("(no ticket) Testing for mail adress %s", from_mail)
	for line in database.cursor.fetchall():
		regex = line[0]
		LOGGER.debug("Found regex: %s", regex)
		if (re.match(regex, from_mail)):
			return True

	return False


def set_status(ticket_id, status_name):
	query = ("UPDATE Tickets SET Status = (SELECT StatusID FROM Status "
		"WHERE Name=? LIMIT 1) WHERE TicketID= ?")
	database.cursor.execute(query, (status_name, ticket_id))

#######################################
### COMMANDS WITHOUT DATABASE ACCESS###
#######################################

def get_references(email):
	search = []
	if ("In-Reply-To" in email.keys()):
		search.append(email['In-Reply-To'])

	if ("References" in email.keys()):
		search += email['References'].split()

	return search

def strip_to_address(from_email):
	# output substring between < >
	return from_email[from_email.find("<")+1:from_email.find(">")]


def check_command(email):
	if (email.is_multipart()):
		first_line = email.get_payload(0).as_string().splitlines()[0]
	else:
		first_line = email.get_payload().splitlines()[0]

	LOGGER.debug(first_line)

	return first_line


def write_email(content, to, subject, from_mail=config.EMAIL_FROM):
	msg = MIMEText(content)
	msg['From'] = from_mail
	msg['To'] = to
	msg['Subject'] = "Featuretracker " + subject

	process = Popen(config.SENDMAIL, stdin=PIPE, universal_newlines=True)
	process.communicate(msg.as_string())


###################################
###     PROCESSING COMMANDS     ###
###################################

def process_email_no_references(email):
	queue_id = search_queue_by_email(email)
	if (queue_id == -1):
		if (email['Subject'].startswith("list open")):
			queue_name = email['Subject'][10:]
			query = "SELECT QueueID FROM Queue WHERE Name=?"
			database.cursor.execute(query, (queue_name, ))

			res = database.cursor.fetchone()

			if (res != None):
				queue_id = res[0]

				if (check_admin(strip_to_address(email['from']), queue_id)):

					email_body = list_open_tickets(queue_id)
					# get e-mail to.
					query = "SELECT value FROM Message_to_Queue WHERE identifier='to' and QueueID = ?"
					database.cursor.execute(query, (queue_id, ))
					to = database.cursor.fetchone()[0]

					write_email(email_body, to, "Open Tickets")

					return

		LOGGER.debug("Failed to determine queue. Exit")
		return errors.NO_QUEUE

	if (check_admin(strip_to_address(email['from']), queue_id)):
		if (email['Subject'] == "list open"):
			LOGGER.debug("List open tickets requested, writing email")
			email_body = list_open_tickets(queue_id)
			# get e-mail to.
			query = "SELECT value FROM Message_to_Queue WHERE identifier='to' and QueueID = ?"
			database.cursor.execute(query, (queue_id, ))
			to = database.cursor.fetchone()[0]

			write_email(email_body, to, "Open Tickets")


			return

	if (check_noticket(strip_to_address(email['from']), queue_id)):
		LOGGER.info("Ticket from no ticket address. Don't create ticket")
		return

	LOGGER.info("Create new ticket")
	ticket_id = create_ticket(email['from'], queue_id, email['subject'])
	save_message(email)
	link_message_ticket(email['message-id'], ticket_id)

def process_email_with_ticket(email, ticket_id):
	LOGGER.debug("Ticket-Id found %s", ticket_id)
	queue_id = get_queue_id_from_ticket_id(ticket_id)
	LOGGER.debug("Check if email is from queue-admin")

	if (check_admin(strip_to_address(email['from']), queue_id)):
		LOGGER.debug("An admin is answering")


		if (check_autoclose(queue_id)):
			LOGGER.debug("Auto close is activated for the queue")
			query = "SELECT Originator FROM Tickets WHERE TicketID = ?"
			database.cursor.execute(query, (ticket_id,))
			originator = strip_to_address(database.cursor.fetchone()[0])
			LOGGER.debug("email To: %s originator: %s", email['To'], originator)

			if (originator in email['To']):
				LOGGER.info("Auto close ticket.")
				set_status(ticket_id, 'Closed')
		if (check_command(email) == "ignore"):
			LOGGER.info("Command received to ignore ticket.")
			set_status(ticket_id, 'Ignored')


	LOGGER.debug("Add message to ticket")
	save_message(email)
	link_message_ticket(email['message-id'], ticket_id)


def process_email(stream=sys.stdin):
	try:
	#	email = Parser().parse(sys.stdin)
		input_stream = io.TextIOWrapper(stream.buffer, errors='ignore')
		email = e.message_from_file(input_stream)
	#	email = e.message_from_file(sys.stdin)
	except UnicodeDecodeError:
		LOGGER.warning("Unicode Decode error. exit")
		return errors.ENCODING

	LOGGER.debug(email.keys())

	if ("Message-ID" not in email.keys()):
		LOGGER.debug("no message id in mail. exit")
		return errors.NO_MESSAGE_ID

	LOGGER.info("Processing %s", email['Message-ID'])

	if check_existence(email['Message-ID']) == True:
		return errors.ALREADY_PROCESSED_EMAIL

	# get references
	references = get_references(email)

	if (references == []):
		LOGGER.debug("No references found.")
		process_email_no_references(email)

	else:
		LOGGER.debug("References found %s", references)
		LOGGER.debug("Search ticket id for references")
		ticket_id = search_ticket_id_by_references(references)

		if (ticket_id > 0):
			process_email_with_ticket(email, ticket_id)
		else:
			LOGGER.debug("No Ticket found")
			process_email_no_references(email)



LOGGER = logging.getLogger("featuretracker")

if __name__ == "__main__":

	logging.basicConfig(level=logging.DEBUG, filename=config.BASE_DIR + "log")
	process_email()

	database.connection.commit()
	database.connection.close()
