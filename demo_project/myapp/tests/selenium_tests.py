import os
import shutil

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from myapp.models import MyModel

__all__ = [
    'InstantTests',
    'OneFailTests',
]

LIPSUM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat "
    "cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
)

class TestsBase(StaticLiveServerTestCase):
    selenium = None
    path = os.path.dirname(__file__)

    @classmethod
    def setUpClass(cls):
        super(TestsBase, cls).setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(0)
        cls.delete_media_directory()

    def setUp(self):
        super(TestsBase, self).setUp()
        self.delete_all_mymodels()

    @classmethod
    def tearDownClass(cls):
        super(TestsBase, cls).tearDownClass()
        cls.selenium.quit()
        cls.delete_media_directory()

    @classmethod
    def full_path(cls, relative_to_tests):
        return os.path.realpath(os.path.join(cls.path, relative_to_tests))

    def wait(self, seconds=0.05):
        try:
            WebDriverWait(self.selenium, seconds).until(lambda driver: False)
        except TimeoutException:
            pass

    @classmethod
    def delete_media_directory(cls):
        try:
            shutil.rmtree(cls.full_path('../../media'))
        except OSError:
            pass

    @classmethod
    def delete_all_mymodels(cls):
        MyModel.objects.all().delete()

    @classmethod
    def _lipsum(cls, index):
        return LIPSUM.split()[index - 1]

    @classmethod
    def _file(cls, index):
        return cls.full_path('files/{}.png'.format(index))

    def _fill_fields(self, name_prefix, content="1"):
        text = self._lipsum(int(content))
        file_path = self._file(int(content))
        self.wait()
        field_text = self.selenium.find_element_by_name("{}_text".format(name_prefix))
        field_text.send_keys(text)
        self.wait()
        field_input = self.selenium.find_element_by_name("{}_file".format(name_prefix))
        field_input.send_keys(file_path)

    def _fill_required(self, content):
        return self._fill_fields("required", content)

    def _fill_optional(self, content):
        return self._fill_fields("optional", content)

    def _fill_description(self, content):
        self.wait()
        description_input = self.selenium.find_element_by_name("description")
        description_input.clear()
        description_input.send_keys(content)

    def _clear(self, name_prefix, do_mark):
        self.wait()
        field_text = self.selenium.find_element_by_name("{}_text".format(name_prefix))
        field_text.clear()
        if not do_mark:
            field_text.send_keys("unmarked...")
        self.wait()
        clear_checkbox = self.selenium.find_element_by_id("{}_file-clear_id".format(name_prefix))
        if clear_checkbox.is_selected() != do_mark:
            clear_checkbox.click()

    def _clear_required(self):
        self._clear("required", True)

    def _clear_optional(self):
        self._clear("optional", True)

    def _unclear_required(self):
        self._clear("required", False)

    def _unclear_optional(self):
        self._clear("optional", False)

    def _is_marked_clear(self, name_prefix):
        clear_checkbox = self.selenium.find_element_by_id("{}_file-clear_id".format(name_prefix))
        return clear_checkbox.is_selected()

    def _assert_required_marked_clear(self):
        self.assertTrue(self._is_marked_clear("required"))

    def _assert_optional_marked_clear(self):
        self.assertTrue(self._is_marked_clear("optional"))

    def _assert_required_not_marked_clear(self):
        self.assertFalse(self._is_marked_clear("required"))

    def _assert_optional_not_marked_clear(self):
        self.assertFalse(self._is_marked_clear("optional"))

    def _submit(self):
        self.wait()
        submit_button = self.selenium.find_element_by_xpath('//input[@type="submit"]')
        submit_button.send_keys(Keys.NULL)
        self.wait()
        submit_button.click()

    def _assert_uploaded(self, content):
        self.selenium.find_element_by_link_text("{}.png".format(content))

    def _assert_not_uploaded(self, content):
        self.assertRaises(
                NoSuchElementException,
                self.selenium.find_element_by_link_text,
                "{}.png".format(content)
        )

    def _assert_message(self, message):
        self.selenium.find_element_by_xpath(
                "/html/body/ul[@class='messages']/li[contains(text(), '{}')]".format(message))

    def _assert_failed(self, name_prefix, message):
        field_positions = {
            'description': 1,
            'required': 3,
            'optional': 5,
        }
        self.selenium.find_element_by_xpath(
            "/html/body/form/ul/li[{position}]/ul[@class='errorlist']/li[contains(text(), '{message}')]".format(
                message=message,
                position=field_positions[name_prefix],
        ))

    def _assert_not_failed(self, name_prefix, message):
        self.assertRaises(
            NoSuchElementException,
            self._assert_failed,
            name_prefix,
            message
        )

class InstantTests(TestsBase):
    def _create_instantly(self):
        self._fill_description('Create instantly')
        self._fill_required(1)
        self._fill_optional(2)
        self._submit()
        self._assert_message("Created MM01")
        self._assert_uploaded(1)
        self._assert_uploaded(2)
        self.wait(1)

    def _clear_instantly(self):
        self._clear_optional()
        self._submit()
        self._assert_message("Updated MM01")
        self._assert_uploaded(1)
        self._assert_not_uploaded(2)
        self.wait(1)

    def test_instantly(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/create/'))
        self._create_instantly()
        self.selenium.get(self.selenium.current_url)
        self._clear_instantly()


class OneFailTests(TestsBase):
    def _fail_create(self):
        self._fill_description('')
        self._fill_required(1)
        self._fill_optional(2)
        self._submit()
        self._assert_failed("description", "This field is required")
        self._assert_not_failed("required", "This field is required")
        self._assert_not_failed("optional", "This field is required")
        self.wait(1)

    def _succeed_create(self):
        self._fill_description('Failed once')
        self._submit()
        self._assert_message("Created MM")
        self._assert_uploaded(1)
        self._assert_uploaded(2)
        self.wait(1)

    def _fail_clear(self):
        self._clear_required()
        self._clear_optional()
        self._submit()
        self._assert_uploaded(1)
        self._assert_uploaded(2)
        self._assert_required_marked_clear()
        self._assert_optional_marked_clear()
        self._assert_failed("required", "This field cannot be blank")
        self._assert_not_failed("optional", "This field cannot be blank")
        self.wait(1)

    def _succeed_clear(self):
        self._unclear_required()
        self._submit()
        self._assert_message("Updated MM")
        self._assert_uploaded(1)
        self._assert_not_uploaded(2)
        self.wait(1)

    def test_one_fail(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/create/'))
        self._fail_create()
        self._succeed_create()
        self.selenium.get(self.selenium.current_url)
        self._fail_clear()
        self._succeed_clear()
