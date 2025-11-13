import os


class ProjectData():
	target = None

	mainModule = ""
	allModules = {}
	allBPs = {}

	# def __init__(self, mainModule):
	def __init__(self):
		super().__init__()

		# self.mainModule = mainModule
		# self.allModules.update({mainModule: {}})

	def addModule(self, module, isMainModule=False):
		filename = os.path.basename(module)
		if isMainModule:
			self.mainModule = {"file": filename, "path": module}
		self.allModules.update({len(self.allModules): {"file": filename, "path": module}})

	def addBreakpoint(self, bp):
		# len(self.allBPs)
		locs = []
		for bl in bp:
			locs.append({"blId": str(bp.GetID()) + "." + str(bl.GetID()),
						 "addr": hex(bl.GetAddress().GetLoadAddress(self.target))})
		self.allBPs.update({bp.GetID(): {"bpId": bp.GetID(), "name": "Dummy Name", "enabled": bp.IsEnabled(),
										 "locations": locs}})  # bp.GetName()

	def updateBreakpoint(self, bp):
		locs = []
		for bl in bp:
			locs.append({"blId": str(bp.GetID()) + "." + str(bl.GetID()),
						 "addr": hex(bl.GetAddress().GetLoadAddress(self.target))})
		self.allBPs.update(
			{bp.GetID(): {"bpId": bp.GetID(), "name": "Dummy Name", "enabled": bp.IsEnabled(),
						  "locations": locs}})  # bp.GetName()

	def removeBreakpoint(self, bp):
		if bp.GetID() in self.allBPs.keys():
			self.allBPs.pop(bp.GetID())

	def to_dict(self):
		return {
			"mainModule": self.mainModule,
			"allModules": self.allModules,
			"allBPs": self.allBPs
		}
