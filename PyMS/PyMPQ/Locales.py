
LOCALE_CHOICES = (
	('Neutral (English)', 0),
	('Chinese (Taiwan)', 1028),
	('Czech', 1029),
	('German', 1031),
	('English (US)', 1032),
	('Spanish', 1034),
	('French', 1036),
	('Italian', 1040),
	('Japanese', 1041),
	('Korean', 1042),
	('Polish', 1045),
	('Portuguese', 1046),
	('Russian', 1049),
	('English (UK)', 2056),
	('Other', None)
)

def find_locale_index(find_locale):
	for index,(_, locale) in enumerate(LOCALE_CHOICES):
		if find_locale == locale or locale == None:
			return index
