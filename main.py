from email.parser import Parser
import sys

import database



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
		print("E-Mail already in Database. Exit")
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
		print("Could not determine status id for Status Open. Exit.")
		sys.exit()
	status_id = val[0]

	query = "INSERT INTO Tickets (Status, Originator, Queue, Subject, opened) VALUES (?,?,?,?, datetime('now'))"
	database.cursor.execute(query, (status_id, originator, queue_id, subject))

	#TODO: none sqlite way
	query = "SELECT last_insert_rowid()"
	database.cursor.execute(query)
	
	return database.cursor.fetchone()[0]


def process_email():
	email = Parser().parse(sys.stdin)

	print(email.keys())
	
	if ("Message-ID" not in email.keys()):
		print("no message id in mail. exit")
		sys.exit()
	print("Processing %s" % email['Message-ID'])
	check_existence(email['Message-ID'])

	# get references
	references = get_references(email)

	if (references == []):
		print("No references found.")
		
		queue_id = search_queue_by_email(email)	
		if (queue_id == -1):
			print("Failed to determine queue. Exit")
			sys.exit()
		print("Create new ticket")
		ticket_id = create_ticket(email['from'], queue_id, email['subject'])
		save_message(email)
		link_message_ticket(email['message-id'],ticket_id)


	else:
		print("References found %s" % references)
		print("Search ticket id for references")
		ticket_id = search_ticket_id_by_references(references)

		if (ticket_id > 0):
			print("Ticket-Id found %s" % ticket_id)
			print("Add message to ticket")

			save_message(email)
			link_message_ticket(email['message-id'],ticket_id)

		else:
			print("No Ticket found")
			
			queue_id = search_queue_by_email(email)	
			if (queue_id == -1):
				print("Failed to determine queue. Exit")
				sys.exit()
			
			print("Create new ticket")
			ticket_id = create_ticket(email['from'], queue_id, email['subject'])
			save_message(email)
			link_message_ticket(email['message-id'],ticket_id)


if __name__ == "__main__":
	process_email()
	database.connection.commit()
	database.connection.close()
