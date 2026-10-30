
from ..FileFormats.MPQ.MPQ import MPQLocale

LOCALE_CHOICES: tuple[tuple[str, int | None], ...] = (
	('Neutral (English)', MPQLocale.neutral),
	('Chinese (Taiwan)', MPQLocale.chinese),
	('Czech', MPQLocale.czech),
	('German', MPQLocale.german),
	('English (US)', MPQLocale.english),
	('Spanish', MPQLocale.spanish),
	('French', MPQLocale.french),
	('Italian', MPQLocale.italian),
	('Japanese', MPQLocale.japanese),
	('Korean', MPQLocale.korean),
	('Polish', MPQLocale.polish),
	('Portuguese', MPQLocale.portuguese),
	('Russian', MPQLocale.russian),
	('English (UK)', MPQLocale.english_uk),
	('Other', None)
)

def find_locale_index(find_locale: int) -> int:
	for index,(_, locale) in enumerate(LOCALE_CHOICES):
		if locale == find_locale:
			return index
	# Locales without their own entry resolve to the trailing 'Other' entry
	return len(LOCALE_CHOICES) - 1
