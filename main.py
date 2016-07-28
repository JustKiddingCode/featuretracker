from email.parser import Parser
import sys
import re
import logging

from email.mime.text import MIMEText
from subprocess import Popen, PIPE

import database
#import commands

# Really sendmail

#sendmail_commad = "/usr/sbin/sendmail"
#sendmail_opts = ["-t", "-oi"]



# For Testing, just print out

sendmail_command = "/bin/cat"
sendmail_opts = []

sendmail = [sendmail_command] + sendmail_opts


emailFrom = "Featuretracker <featuretracker@fsmi.uka.de>"

def list_ticket(status_id,queue_id):
	query = "SELECT Originator, opened, Subject FROM Tickets WHERE Queue = ? AND Status= ?"
	database.cursor.execute(query, (queue_id,status_id))
	
	ticket_list = ""

	for row in database.cursor.fetchall():
		ticket_list += "%s %s %s \n\n" % (row[0], row[1], row[2]) 
	
	return ticket_list


def search_ticket_id_by_references(references):
	query = "Select TicketID FROM Link_Ticket_Message WHERE MessageID in (%s)" % ','.join('?' * len(references))

	database.cursor.execute(query, references)
	val = database.cursor.fetchone()

	if (val == None):
		return -1
	else:
		return val[0]


def get_references(email):
	search = []
	if ("In-Reply-To" in email.keys()):
		search.append(email['In-Reply-To'])
	
	if ("References" in email.keys()):
		search += email['References'].split()
	
	return search

def check_existence(message_id):
	query = "SELECT Count(*) FROM Emails WHERE MessageID = ?"
	database.cursor.execute(query, (message_id, ))
	count = database.cursor.fetchone()[0]

	if (count > 0):
		logger.debug("E-Mail already in Database. Exit")
		sys.exit()

def save_message(email):
	query = "INSERT INTO Emails (MessageID, Content) VALUES (?,?)"
	database.cursor.execute(query, (email['message-id'], str(email)))


def link_message_ticket(message_id, ticket_id):
	query = "INSERT INTO Link_Ticket_Message (TicketID, MessageID) VALUES (?,?)"
	database.cursor.execute(query, (ticket_id, message_id))

def search_queue_by_email(email):
	# TO
	query = "SELECT QueueID FROM Message_to_Queue WHERE identifier='to' and value = ?"

	database.cursor.execute(query, (email['To'], ))
	val = database.cursor.fetchone()
	if (val == None):
		return -1
	return val[0]

def create_ticket(originator, queue_id, subject):
	# Get open status id
	query = "SELECT StatusID FROM Status WHERE Name = 'Open'"
	database.cursor.execute(query)
	val = database.cursor.fetchone()
	if (val == None):
		logger.debug("Could not determine status id for Status Open. Exit.")
		sys.exit()
	status_id = val[0]

	query = "INSERT INTO Tickets (Status, Originator, Queue, Subject, opened) VALUES (?,?,?,?, datetime('now'))"
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

def strip_to_address(from_email):
	# output substring between < >
	return from_email[from_email.find("<")+1:from_email.find(">")]


def check_admin(from_email, queue_id):
	query = "SELECT Email_Regex FROM Queue_Admin WHERE QueueID = ?"
	database.cursor.execute(query, (queue_id, ))
	
	logger.debug("Testing for mail adress %s" % from_email) 
	for line in database.cursor.fetchall():
		regex = line[0]
		logger.debug("Found regex: %s" % regex)
		if (re.match(regex, from_email)):
			return True

	return False;

def check_autoclose(queue_id):
	query = "SELECT autoclose FROM Queue WHERE QueueID = ?"
	database.cursor.execute(query, (queue_id, ))

	val = database.cursor.fetchone() 
	return (val[0] == 1)

def check_command(email):
	if (email.is_multipart()):
		firstLine = email.get_payload(0).as_string().splitlines()[0]
	else:
		firstLine = email.get_payload().splitlines()[0]
	
	logger.debug(firstLine)
	
	return firstLine

def list_open_tickets(queue_id):
	query = "SELECT StatusID From Status WHERE Name=?"
	database.cursor.execute(query, ("Open",))
	status_id = database.cursor.fetchone()[0]
	email_body = list_ticket(status_id, queue_id)

	return email_body

def write_email(content, to, subject, from_mail = emailFrom):
	msg = MIMEText(email_body)
	msg['From'] = "Featuretracker <featuretracker@fsmi.uka.de>"
	msg['To'] = to
	msg['Subject'] = "Open Tickets"	
		
	p = Popen(sendmail, stdin=PIPE, universal_newlines=True)
	p.communicate(msg.as_string())
			
def check_noticket(mail, queue_id):
	
	query = "SELECT Email_Regex FROM Queue_NoTicket WHERE QueueID = ?"
	database.cursor.execute(query, (queue_id, ))
	
	logger.debug("(no ticket) Testing for mail adress %s" % from_email) 
	for line in database.cursor.fetchall():
		regex = line[0]
		logger.debug("Found regex: %s" % regex)
		if (re.match(regex, from_email)):
			return True

	return False;

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

		logger.debug("Failed to determine queue. Exit")
		sys.exit()
	
	if (check_admin(strip_to_address(email['from']), queue_id)):
		if (email['Subject'] == "list open"):
			
			email_body = list_open_tickets(queue_id)
			# get e-mail to.
			query = "SELECT value FROM Message_to_Queue WHERE identifier='to' and QueueID = ?"
			database.cursor.execute(query, (queue_id, ))
			to = database.cursor.fetchone()[0]
			
			write_email(email_body, to, "Open Tickets")
			

			return

	if (check_noticket(strip_to_address(email['from']), queue_id)):
		logger.info("Ticket from no ticket address. Don't create ticket")
		return

	logger.info("Create new ticket")
	ticket_id = create_ticket(email['from'], queue_id, email['subject'])
	save_message(email)
	link_message_ticket(email['message-id'],ticket_id)

def set_status(ticket_id, status_name):
	query = "UPDATE Tickets SET Status = (SELECT StatusID FROM Status WHERE Name=? LIMIT 1) WHERE TicketID= ?"
	database.cursor.execute(query, (status_name, ticket_id ))
	
def process_email_with_ticket(email, ticket_id):
	logger.debug("Ticket-Id found %s" % ticket_id)
	queue_id = get_queue_id_from_ticket_id(ticket_id)
	logger.debug("Check if email is from queue-admin")

	if (check_admin(strip_to_address(email['from']), queue_id)):
		logger.debug ("An admin is answering")


		if (check_autoclose(queue_id)):
			logger.debug("Auto close is activated for the queue")
			query = "SELECT Originator FROM Tickets WHERE TicketID = ?"
			database.cursor.execute(query, (ticket_id,))
			originator = strip_to_address(database.cursor.fetchone()[0])
			logger.debug("email To: %s originator: %s" % (email['To'], originator))

			if (originator in email['To']) :
				logger.info("Auto close ticket.")
				set_status(ticket_id, 'Closed')
		if (get_command(email) == "ignore"):
			logger.info("Command received to ignore ticket.")
			set_status(ticket_id, 'Ignored')
	
	
	logger.debug("Add message to ticket")
	save_message(email)
	link_message_ticket(email['message-id'],ticket_id)


def process_email():
	email = Parser().parse(sys.stdin)

	logger.debug(email.keys())
	
	if ("Message-ID" not in email.keys()):
		logger.debug("no message id in mail. exit")
		sys.exit()
	logger.info("Processing %s" % email['Message-ID'])
	check_existence(email['Message-ID'])

	# get references
	references = get_references(email)

	if (references == []):
		logger.debug("No references found.")
		
		process_email_no_references(email)

	else:
		logger.debug("References found %s" % references)
		logger.debug("Search ticket id for references")
		ticket_id = search_ticket_id_by_references(references)

		if (ticket_id > 0):
			process_email_with_ticket(email, ticket_id)
		else:
			logger.debug("No Ticket found")
			process_email_no_references(email)	


if __name__ == "__main__":

	logger = logging.getLogger("featuretracker")
	logging.basicConfig(level=logging.DEBUG,filename="log")
	process_email()

	database.connection.commit()
	database.connection.close()
