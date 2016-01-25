from functools import partial

from django.test import TestCase
from .widget import NormalizedFileInput


class RenderStateTestCase(TestCase):

    def setUp(self):
        self.widget = NormalizedFileInput()
        self.field_name = "file_field_name"

    def test_empty(self):
        value = None
        output = self.widget.render(self.field_name, value)
        self.assertIn('type="file"', output)
        self.assertNotIn('type="checkbox"', output)
        self.assertNotIn('type="text"', output)


class ValueStateTestCase(TestCase):

    def setUp(self):
        self.widget = NormalizedFileInput()
        self.field_name = "file_field_name"
        self.render = partial(self.widget.render, name=self.field_name)

    def test_empty(self):
        data = {}
        files = {}
        value = self.widget.value_from_datadict(data, files, self.field_name)
        self.assertIsNone(value)

