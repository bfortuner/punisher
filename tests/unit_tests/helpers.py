def createMatcher(self, regex):
	def matchCheck(argument):
		self.assertTrue(regex.match(argument))
	return matchCheck
