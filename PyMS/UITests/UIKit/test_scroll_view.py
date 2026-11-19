from ..harness import UITestCase

from ...Utilities import UIKit as UI

Fill = UI.ScrollView.Fill


class Test_ScrollView(UITestCase):
	# A 300x300 window, so the visible area is a bit under 300x300
	def _scroll_view(self, content_width: int, content_height: int, *, fill_width: UI.ScrollView.Fill = Fill.none, fill_height: UI.ScrollView.Fill = Fill.none) -> tuple[UI.MainWindow, UI.ScrollView]:
		window = self.make_window(UI.MainWindow)
		window.geometry('300x300')
		scroll_view = UI.ScrollView(window, fill_width=fill_width, fill_height=fill_height)
		scroll_view.pack(fill=UI.BOTH, expand=1)
		UI.Frame(scroll_view.content_view, width=content_width, height=content_height).pack()
		self.pump(window)
		return (window, scroll_view)

	def _content_size(self, scroll_view: UI.ScrollView) -> tuple[int, int]:
		return (scroll_view.content_view.winfo_width(), scroll_view.content_view.winfo_height())

	def test_none_keeps_the_requested_size(self) -> None:
		_, small = self._scroll_view(100, 50)
		self.assertEqual(self._content_size(small), (100, 50))
		_, big = self._scroll_view(500, 600)
		self.assertEqual(self._content_size(big), (500, 600))
		self.assertEqual(big.content_size(), (500, 600))

	def test_exact_width_matches_the_viewport_width(self) -> None:
		for content_width in (100, 500):
			_, scroll_view = self._scroll_view(content_width, 50, fill_width=Fill.exact)
			viewport_width, _ = scroll_view.viewport_size()
			self.assertEqual(self._content_size(scroll_view), (viewport_width, 50))
			self.assertEqual(scroll_view.content_size(), (viewport_width, 50))

	def test_exact_height_matches_the_viewport_height(self) -> None:
		for content_height in (50, 600):
			_, scroll_view = self._scroll_view(100, content_height, fill_height=Fill.exact)
			_, viewport_height = scroll_view.viewport_size()
			self.assertEqual(self._content_size(scroll_view), (100, viewport_height))
			self.assertEqual(scroll_view.content_size(), (100, viewport_height))

	def test_minimum_grows_content_to_the_viewport(self) -> None:
		_, scroll_view = self._scroll_view(100, 50, fill_width=Fill.minimum, fill_height=Fill.minimum)
		self.assertEqual(self._content_size(scroll_view), scroll_view.viewport_size())

	def test_minimum_scrolls_content_bigger_than_the_viewport(self) -> None:
		_, scroll_view = self._scroll_view(500, 600, fill_width=Fill.minimum, fill_height=Fill.minimum)
		viewport_width, viewport_height = scroll_view.viewport_size()
		self.assertLess(viewport_width, 500)
		self.assertLess(viewport_height, 600)
		self.assertEqual(self._content_size(scroll_view), (500, 600))
		self.assertEqual(scroll_view.content_size(), (500, 600))

	def test_minimum_follows_content_added_later(self) -> None:
		window, scroll_view = self._scroll_view(100, 50, fill_width=Fill.minimum, fill_height=Fill.minimum)
		UI.Frame(scroll_view.content_view, width=100, height=600).pack()
		self.pump(window)
		viewport_width, _ = scroll_view.viewport_size()
		self.assertEqual(self._content_size(scroll_view), (viewport_width, 650))
		self.assertEqual(scroll_view.content_size(), (viewport_width, 650))

	def test_axes_fill_independently(self) -> None:
		_, scroll_view = self._scroll_view(500, 50, fill_width=Fill.exact, fill_height=Fill.minimum)
		self.assertEqual(self._content_size(scroll_view), scroll_view.viewport_size())
		_, scroll_view = self._scroll_view(100, 600, fill_width=Fill.minimum, fill_height=Fill.exact)
		self.assertEqual(self._content_size(scroll_view), scroll_view.viewport_size())
