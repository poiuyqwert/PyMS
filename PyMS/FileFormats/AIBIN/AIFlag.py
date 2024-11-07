
class AIFlag:
	requires_location = (1 << 0)
	staredit_hidden = (1 << 1)
	broodwar_only = (1 << 2)

	@staticmethod
	def flags(requires_location: bool, staredit_hidden: bool, broodwar_only: bool) -> int:
		flags = 0
		if requires_location:
			flags |= AIFlag.requires_location
		if staredit_hidden:
			flags |= AIFlag.staredit_hidden
		if broodwar_only:
			flags |= AIFlag.broodwar_only
		return flags
