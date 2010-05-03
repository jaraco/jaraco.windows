import os
from win32com.client import Dispatch, constants

from jaraco.util.filesystem import save_to_file, replace_extension

class Converter(object):
	"""
	An object that will convert a Word-readable file to one of the Word-
	savable formats (defaults to PDF).
	
	Requires Microsoft Word 2007 or later.
	"""
	target_format = getattr(constants, 'wdFormatPDF', 17)

	def __init__(self):
		self.word = Dispatch('Word.Application')

	def convert(self, docfile_string):
		"""
		Take a string (in memory) and return it as a string of the
		target format (also as a string in memory).
		"""
		with save_to_file(docfile_string) as docfile:
			doc = self.word.Documents.Open(docfile)
			# if I don't put a pdf extension on it, Word will
			pdffile = replace_extension('.pdf', docfile)
			res = doc.SaveAs(pdffile, self.target_format)
			wdDoNotSaveChanges = getattr(constants, 'wdDoNotSaveChanges', 0)
			doc.Close(wdDoNotSaveChanges)
			content = open(pdffile, 'rb').read()
			os.remove(pdffile)
		return content

	__call__ = convert

	def __del__(self):
		self.word.Quit()
