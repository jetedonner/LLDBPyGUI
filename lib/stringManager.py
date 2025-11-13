import enum


# "listener_"
def get_string(pattern, *params):
	if params:
		# print(f"WEEEEEEEEELLLLLLLLCCCCCCCCCOOOOOOOOMMMMMMMMMMEEEEEEEEE 2 params: {sParam} / {pattern.value[0]}")
		return format_with_args(pattern.value[0], *params)
	return "-error-"


def format_with_args(template, *args):
	return template.format(*args)


# from PyQt6.QtCore import QObject

class StringManager():
	# setHelper = None

	def __init__(self):  # , driver, setHelper):
		super().__init__()

		# self.setHelper = setHelper

	def getString(self, pattern, *params):
		sParam = ""
		if params:
			print(f"WEEEEEEEEELLLLLLLLCCCCCCCCCOOOOOOOOMMMMMMMMMMEEEEEEEEE 2 params: {sParam} / {pattern.value[0]}")
			for i in range(len(params)):
				sParam += ", " + params[i]
			print(f"with args: {self.format_with_args(pattern.value[0], *params)}")
		pass

	def format_with_args(self, template, *args):
		return template.format(*args)


class StringPatterns(enum.Enum):
	listener_pfx = ("listener_", 0)
	teset = ("{1} scored higher than {0} in the test.", 2)
