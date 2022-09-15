
from ...FileFormats.MPQ import MPQ
from ...Utilities.PyMSError import PyMSError

from ..utils import resource_path

import unittest, tempfile, os

class Test_StormLib_Open(unittest.TestCase):
	def test_open_readonly(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		mpq.open(read_only=True)
		self.assertTrue(mpq.is_open())
		self.assertTrue(mpq.is_read_only())
		mpq.close()
		self.assertFalse(mpq.is_open())

	def test_open_editable(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		mpq.open(read_only=False)
		self.assertTrue(mpq.is_open())
		self.assertFalse(mpq.is_read_only())
		mpq.close()
		self.assertFalse(mpq.is_open())

	def test_open_readonly_open_readonly(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		mpq.open(read_only=True)
		mpq.open(read_only=True)
		mpq.close()

	def test_open_editable_open_readonly(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		mpq.open(read_only=False)
		mpq.open(read_only=True)
		mpq.close()

	def test_open_readonly_open_editable(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		mpq.open(read_only=True)
		with self.assertRaises(PyMSError):
			mpq.open(read_only=False)
		mpq.close()

	def test_with(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open():
			self.assertTrue(mpq.is_open())
		self.assertFalse(mpq.is_open())

	def test_with_auto_close(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		mpq.open()
		self.assertTrue(mpq.is_open())
		with mpq.open():
			self.assertTrue(mpq.is_open())
		self.assertTrue(mpq.is_open())
		with mpq.open():
			self.assertTrue(mpq.is_open())
		self.assertTrue(mpq.is_open())
		mpq.close()
		self.assertFalse(mpq.is_open())

	def test_with_auto_close_override(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		mpq.open()
		self.assertTrue(mpq.is_open())
		with mpq.open():
			self.assertTrue(mpq.is_open())
		self.assertTrue(mpq.is_open())
		with mpq.open() as ctx:
			ctx.auto_close = True
			self.assertTrue(mpq.is_open())
		self.assertFalse(mpq.is_open())

	def test_used_block_count(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open():
			self.assertEqual(mpq.used_block_count(), 5)

	def test_list_files(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open():
			files = mpq.list_files()
		self.assertEqual(
			sorted(files),
			sorted([
				MPQ.MPQFileEntry(file_name=MPQ.MPQInternalFile.listfile, locale=MPQ.MPQLocale.neutral),
				MPQ.MPQFileEntry(file_name=MPQ.MPQInternalFile.listfile, locale=MPQ.MPQLocale.spanish),
				MPQ.MPQFileEntry(file_name='test.txt', locale=MPQ.MPQLocale.neutral),
				MPQ.MPQFileEntry(file_name='test.txt', locale=MPQ.MPQLocale.spanish),
				MPQ.MPQFileEntry(file_name='File00000004.xxx', locale=MPQ.MPQLocale.spanish),
			])
		)

	def test_listfile_open_list_files(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		mpq.add_listfile(resource_path('listfile.txt', __file__))
		with mpq.open():
			files = mpq.list_files()
		self.assertEqual(
			sorted(files),
			sorted([
				MPQ.MPQFileEntry(file_name=MPQ.MPQInternalFile.listfile, locale=MPQ.MPQLocale.neutral),
				MPQ.MPQFileEntry(file_name=MPQ.MPQInternalFile.listfile, locale=MPQ.MPQLocale.spanish),
				MPQ.MPQFileEntry(file_name='test.txt', locale=MPQ.MPQLocale.neutral),
				MPQ.MPQFileEntry(file_name='test.txt', locale=MPQ.MPQLocale.spanish),
				MPQ.MPQFileEntry(file_name='unknown.txt', locale=MPQ.MPQLocale.spanish),
			])
		)

	def test_open_listfile_list_files(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open():
			mpq.add_listfile(resource_path('listfile.txt', __file__))
			files = mpq.list_files()
		self.assertEqual(
			sorted(files),
			sorted([
				MPQ.MPQFileEntry(file_name=MPQ.MPQInternalFile.listfile, locale=MPQ.MPQLocale.neutral),
				MPQ.MPQFileEntry(file_name=MPQ.MPQInternalFile.listfile, locale=MPQ.MPQLocale.spanish),
				MPQ.MPQFileEntry(file_name='test.txt', locale=MPQ.MPQLocale.neutral),
				MPQ.MPQFileEntry(file_name='test.txt', locale=MPQ.MPQLocale.spanish),
				MPQ.MPQFileEntry(file_name='unknown.txt', locale=MPQ.MPQLocale.spanish),
			])
		)

	def test_has_file(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open():
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.neutral))

	def test_has_file_no_locale_has_neutral(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open():
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.german))

	def test_has_file_no_locale_no_neutral(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open():
			self.assertFalse(mpq.has_file('unknown.txt', MPQ.MPQLocale.german))

	def test_read_file(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open():
			self.assertEqual(mpq.read_file('test.txt', MPQ.MPQLocale.spanish), 'spanish')

	def test_read_file_no_locale_has_neutral(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open():
			self.assertEqual(mpq.read_file('test.txt', MPQ.MPQLocale.german), 'english')

	def test_read_file_no_locale_no_neutral(self):
		mpq = MPQ.StormLibMPQ(resource_path('test.mpq', __file__))
		with mpq.open() and self.assertRaises(PyMSError):
			mpq.read_file('unknown.txt', MPQ.MPQLocale.german)

class Test_StormLib_Create(unittest.TestCase):
	def __init__(self, methodName='runTest'):
		unittest.TestCase.__init__(self, methodName)
		self.path = None # type: str

	def setUp(self):
		self.path = tempfile.mktemp()

	def tearDown(self):
		if os.path.exists(self.path):
			os.unlink(self.path)

	def test_create(self):
		mpq = MPQ.StormLibMPQ(self.path)
		mpq.create(stay_open=False)
		self.assertFalse(mpq.is_open())
		self.assertTrue(os.path.exists(self.path))

	def test_create_stay_open(self):
		mpq = MPQ.StormLibMPQ(self.path)
		mpq.create()
		self.assertTrue(mpq.is_open())
		self.assertFalse(mpq.is_read_only())
		mpq.close()
		self.assertTrue(os.path.exists(self.path))

	def test_open_or_create(self):
		mpq = MPQ.SFMPQ(self.path)
		self.assertFalse(os.path.exists(self.path))
		mpq.open_or_create()
		self.assertTrue(mpq.is_open())
		self.assertFalse(mpq.is_read_only())
		mpq.close()
		self.assertTrue(os.path.exists(self.path))
		mpq.open_or_create()
		self.assertTrue(mpq.is_open())
		self.assertFalse(mpq.is_read_only())
		mpq.close()

	def test_with(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			self.assertTrue(mpq.is_open())
			self.assertFalse(mpq.is_read_only())
		self.assertFalse(mpq.is_open())
		self.assertTrue(os.path.exists(self.path))

	def test_add_file(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_file(resource_path('listfile.txt', __file__), 'test.txt')
			self.assertTrue(mpq.has_file('test.txt'))
			self.assertEqual(mpq.read_file('test.txt'), 'unknown.txt')

	def test_add_file_locale(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_file(resource_path('listfile.txt', __file__), 'test.txt', MPQ.MPQLocale.spanish)
			self.assertFalse(mpq.has_file('test.txt'))
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.spanish))
			self.assertEqual(mpq.read_file('test.txt', MPQ.MPQLocale.spanish), 'unknown.txt')

	def test_add_data(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_data('test', 'test.txt')
			self.assertTrue(mpq.has_file('test.txt'))
			self.assertEqual(mpq.read_file('test.txt'), 'test')

	def test_add_data_locale(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_data('test', 'test.txt', MPQ.MPQLocale.spanish)
			self.assertFalse(mpq.has_file('test.txt'))
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.spanish))
			self.assertEqual(mpq.read_file('test.txt', MPQ.MPQLocale.spanish), 'test')

	def test_rename(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_data('test', 'test.txt')
			self.assertTrue(mpq.has_file('test.txt'))
			mpq.rename_file('test.txt', 'rename.txt')
			self.assertFalse(mpq.has_file('test.txt'))
			self.assertTrue(mpq.has_file('rename.txt'))

	def test_rename_locale(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_data('test', 'test.txt', MPQ.MPQLocale.german)
			mpq.add_data('test', 'test.txt', MPQ.MPQLocale.spanish)
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.german))
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.spanish))
			mpq.rename_file('test.txt', 'rename.txt', MPQ.MPQLocale.spanish)
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.german))
			self.assertFalse(mpq.has_file('test.txt', MPQ.MPQLocale.spanish))
			self.assertTrue(mpq.has_file('rename.txt', MPQ.MPQLocale.spanish))

	def test_change_locale(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_data('test', 'test.txt', MPQ.MPQLocale.spanish)
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.spanish))
			self.assertFalse(mpq.has_file('test.txt', MPQ.MPQLocale.german))
			mpq.change_file_locale('test.txt', MPQ.MPQLocale.spanish, MPQ.MPQLocale.german)
			self.assertFalse(mpq.has_file('test.txt', MPQ.MPQLocale.spanish))
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.german))

	def test_delete(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_data('test', 'test.txt')
			self.assertTrue(mpq.has_file('test.txt'))
			mpq.delete_file('test.txt')
			self.assertFalse(mpq.has_file('test.txt'))

	def test_delete_locale(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_data('test', 'test.txt', MPQ.MPQLocale.german)
			mpq.add_data('test', 'test.txt', MPQ.MPQLocale.spanish)
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.german))
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.spanish))
			mpq.delete_file('test.txt', MPQ.MPQLocale.spanish)
			self.assertTrue(mpq.has_file('test.txt', MPQ.MPQLocale.german))
			self.assertFalse(mpq.has_file('test.txt', MPQ.MPQLocale.spanish))

	def test_compact(self):
		mpq = MPQ.StormLibMPQ(self.path)
		with mpq.create():
			mpq.add_data('test', 'test.txt')
		with mpq.open(read_only=False): # Not sure why it needs to be closed and re-opened (flushed) for the block count to update
			self.assertEqual(mpq.used_block_count(), 2) # `(listfile)` and `test.txt`
			mpq.delete_file('test.txt')
			self.assertEqual(mpq.used_block_count(), 2)
			mpq.compact()
			self.assertEqual(mpq.used_block_count(), 1) # Still has `(listfile)`
