def list(status_id,queue_id):
	query = "SELECT * FROM Tickets WHERE Queue = ? AND Status= ?"
	database.cursor.execute(query, (queue,status))
	
	ticket_list = ""

	for row in database.cursor.fetchall():
		ticket_list += "%s %s %s" % (row['Originator'], row['opened'], row['Subject'])
	
	return ticket_list
