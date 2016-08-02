import unittest
from email.parser import Parser
from tempfile import mkstemp

from main import *
import logging

import subprocess

import sqlite3


class TestUM(unittest.TestCase):

	def setUp(self):
		#change database
		tmpfile = mkstemp()[1]
		init_sql = open("sql/00_init_sqlite3.sql", 'r')

		initstr = ["sqlite3",tmpfile]
		#init database
		p = subprocess.Popen(initstr, stdin=init_sql)	
		p.wait()

		database.connection = sqlite3.connect(tmpfile)
		database.cursor = database.connection.cursor()


		# add queue
		database.cursor.execute("INSERT INTO Queue ( QueueID, Name, autoclose ) VALUES (1, 'Testing', 0)")
		database.cursor.execute("INSERT INTO Queue ( QueueID, Name, autoclose ) VALUES (2, 'Testing Second', 1)")

		logging.basicConfig(level=logging.DEBUG)

	def test_process_email(self):
		f = open("test/data/43:2,")
		# more setup of database
		process_email(stream=f)
		# TODO: Actual testing

	def test_check_autoclose(self):
		self.assertEqual(check_autoclose(1), False)	
		self.assertEqual(check_autoclose(2), True)	

	
	def test_strip_to_address(self):
		self.assertEqual( strip_to_address("bla bla <ente@123.com>"), 'ente@123.com')
		self.assertEqual( strip_to_address("<fixme@fix.info.test> "), "fixme@fix.info.test")

	def test_get_references(self):
		email1 = Parser().parsestr(
			'From: <test1@example.com>\n'
			'To: <test2@example.com>\n'
			'Subject: Testing\n'
			'Message-ID: 12345@example.com\n'
			'\n'
			'Hi\n')

		email2 = Parser().parsestr(
			'From: <test1@example.com>\n'
			'To: <test2@example.com>\n'
			'Subject: Testing\n'
			'In-Reply-To: 12345@example.com\n'
			'\n'
			'Hi\n')

		email3 = Parser().parsestr(
			'From: <test1@example.com>\n'
			'To: <test2@example.com>\n'
			'Subject: Testing\n'
			'References: 12345@example.com\n'
			'\n'
			'Hi\n')
		
		self.assertEqual ( get_references(email1), [])
		self.assertEqual ( get_references(email2), ['12345@example.com'])
		self.assertEqual ( get_references(email3), ['12345@example.com'])


if __name__ == "__main__":
	unittest.main()
