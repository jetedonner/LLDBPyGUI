import json


class Arm64MnemonicReference:
	data = None

	def __init__(self):
		super().__init__()
		self.loadJSON()

	def loadJSON(self):
		# Open and load the JSON file
		with open("./ARM64.json", "r", encoding="utf-8") as f:
			self.data = json.load(f)

	arrSynonyms = {"SUB (extended register)": "sub",
				   "ADD (extended register)": "add",
				   "MOV (to/from SP)": "mov",
				   "LDR (immediate, SIMD&FP)": "ldr",
				   "STR (immediate, SIMD&FP)": "str"}

	# def getTitleForSynonym(self, synonym):
	#     sRet = ""
	#     return sRet

	def getSynonymForTitle(self, title):
		if self.arrSynonyms.get(title):
			# print(f"self.arrSynonyms.get(title): {self.arrSynonyms.get(title).lower()}")
			return self.arrSynonyms.get(title).lower()
		else:
			return ""

	def getDoc(self, mnemonic):
		bl_instruction = None
		title = ""
		for entry in self.data["encodings"]:
			titleCurrOrig = entry.get("title")
			titleCurr = titleCurrOrig.lower()
			mnemonic = mnemonic.lower()
			if titleCurr == mnemonic or self.getSynonymForTitle(
					titleCurrOrig) == mnemonic:  # (titleCurr == "SUB (extended register)".lower() and "sub" == mnemonic): # self.getSynonymForTitle(titleCurr) == mnemonic:
				# print(f"GOTIT => self.getSynonymForTitle(titleCurr): {self.getSynonymForTitle(titleCurrOrig)} / {titleCurr} / {titleCurrOrig} ....")
				bl_instruction = entry
				break

		# Display the details
		sRet = ""
		if bl_instruction:
			title = bl_instruction["title"]
			# print("Instruction:", bl_instruction["title"])
			# sRet += f'Instruction: {bl_instruction["title"]}\n'
			# print("Description:", bl_instruction["description"])
			sRet += f'Description: {bl_instruction["description"]}\n'
			# print("File:", bl_instruction["file"])
			sRet += f'File: {bl_instruction["file"]}\n'
			# print("ID:", bl_instruction["id"])
			sRet += f'ID: {bl_instruction["id"]}\n'
			# print("\nClasses:")
			sRet += f'Classes:\n'
			for cls in bl_instruction["classes"]:
				# print("  Class Title:", cls["title"])
				sRet += f'  Class Title: {cls["title"]}\n'
				# print("  Fields:")
				sRet += f'  Fields:\n'
				for field_name, field_info in cls["fields"].items():
					# print(f"    {field_name}: {field_info}")
					sRet += f'    {field_name}: {field_info}\n'
				# print("  Encodings:")
				sRet += f'  Encodings:\n'
				for enc in cls["encodings"]:
					# print(f"    ASM: {enc['asm']}")
					sRet += f'    ASM: {enc["asm"]}\n'
					# print(f"    Title: {enc['title']}")
					sRet += f'    Title: {enc["title"]}\n'
		else:
			print(f"{mnemonic} instruction not found.")

		return title, sRet
