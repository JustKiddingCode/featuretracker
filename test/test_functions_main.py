import unittest

from main import *

class TestUM(unittest.TestCase):

	def setUp(self):
		pass
	
	
	def test_strip_to_address(self):
		self.assertEqual( strip_to_address("bla bla <ente@123.com>"), 'ente@123.com')
		self.assertEqual( strip_to_address("<fixme@fix.info.test> "), "fixme@fix.info.test")

if __name__ == "__main__":
	unittest.main()
