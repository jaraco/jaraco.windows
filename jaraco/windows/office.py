import os
from win32com.client import Dispatch, constants

from jaraco.util.filesystem import save_to_file

class Converter(object):
	def __init__(self):
		self.word = Dispatch('Word.Application')

	def convert(self, docfile_string):
		with save_to_file(docfile_string) as docfile:
			doc = self.word.Documents.Open(docfile)
			wdFormatPDF = getattr(constants, 'wdFormatPDF', 17)
			pdffile = docfile+'.pdf' # if I don't put a pdf extension on it, Word will
			res = doc.SaveAs(pdffile, wdFormatPDF)
			wdDoNotSaveChanges = getattr(constants, 'wdDoNotSaveChanges', 0)
			doc.Close(wdDoNotSaveChanges)
			content = open(pdffile, 'rb').read()
			os.remove(pdffile)
		return content

	__call__ = convert

	def __del__(self):
		self.word.Quit()

