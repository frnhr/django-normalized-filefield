import uuid
from os.path import basename

from django.forms.widgets import FileInput, HiddenInput, CheckboxInput
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from .cache import FileCache
from .helpers import make_choices

STATE = make_choices("State", "empty selected current update clear", start_from=1)
INTENT = make_choices("Intent", "noop upload clear")


class NormalizedFileInput(FileInput):
    text_initial = ugettext_lazy('Currently:')
    text_temporary = ugettext_lazy('Selected:')
    text_change = ugettext_lazy('Change:')
    text_clear = ugettext_lazy('Clear')

    inputs_wraps = {
        'file':
            '{file_input}',
        'clear':
            '{clear_checkbox} '
            '<label for="{clear_checkbox_id}">'
            '{text_clear}'
            '</label>',
    }

    template_parts = {
        'input': '{file_wrap}',
        'change': '{text_change} '
                  '{file_input}',
        'initial': '{text_initial} '
                   '<a href="{initial_url}">'
                   '{initial_link_text}'
                   '</a>'
                   '{clear_wrap}'
                   '</span>',
        'temporary': '{text_temporary} '
                     '{temporary_filename} '
                     '{clear_wrap}',
    }

    state_templates = {
        STATE.empty: '{input}',
        STATE.selected: '{temporary}<br />{change}',
        STATE.current: '{initial}<br />{change}',
        STATE.update: '{temporary}<br />{change}',
        STATE.clear: '{initial}<br />{change}',
    }

    # @TODO optimize: don't render cache input when EMPTY or CURRENT, if possible
    template = '{state_template}{cache_input}'
    cache_key = ''
    data = {}
    new_state = None
    past_state = None
    _field_name = None
    _file_cache = None

    def __init__(self, attrs=None):
        super(NormalizedFileInput, self).__init__(attrs)
        self.substitutions = {
            'text_initial': self.text_initial,
            'text_change': self.text_change,
            'text_clear': self.text_clear,
            'file': '',
            'cache': '',
            'clear_checkbox': '',
            'clear_checkbox_id': '',
            'initial_url': '',
            'current': '',
        }

    @property
    def file_cache(self):
        if self._file_cache is None:
            self._file_cache = FileCache()
        return self._file_cache

    def get_data(self):
        """
        Get persistent data for this field.
        This is "state", but calling it "data" to avoid confusion with the state of the field
            (see `self.get_state`)
        :return: dict
        """
        data = self.file_cache.get(self.cache_key)
        if data is None:
            data = self._empty_data()
        return data

    @staticmethod
    def _empty_data():
        return {
            'state': STATE.empty,
            'upload': None,
            'clear': False,
            'initial_url': False,
            'initial_name': False,
        }

    def update_data(self, partial_state):
        if not self.cache_key:
            raise ValueError("Empty cache_key!")
        data = self.file_cache.get(self.cache_key) or self._empty_data()
        data.update(**partial_state)
        self.file_cache.set(self.cache_key, self.field_name, **data)
        return data

    @staticmethod
    def _decide_new_state(past_state, upload, clear):
        # Note: It IS possible to have BOTH `upload` and `clear` arguments set to truthy
        #       This is mainly true for `clear` state
        # Note 2: Order of `if`s under each case matters, it resolves ambiguity
        #         (what to do when both "Clear" is checked AND a file is selected for upload)
        if past_state not in STATE:
            raise ValueError("Invalid STATE: '{}'".format(past_state))
        if past_state == STATE.empty:
            if upload:
                return STATE.selected
            return past_state
        if past_state == STATE.selected:
            if upload:
                return STATE.selected
            if clear:
                return STATE.empty
            return past_state
        if past_state == STATE.current:
            if upload:
                return STATE.update
            if clear:
                return STATE.clear
            return past_state
        if past_state == STATE.update:
            if upload:
                return STATE.update
            if clear:
                return STATE.clear
            return past_state
        if past_state == STATE.clear:
            if upload:
                return STATE.update
            if not clear:
                return STATE.current
            return past_state

    @staticmethod
    def _intent(state):
        if state not in STATE:
            raise ValueError("Invalid STATE: '{}'".format(state))
        return {
            STATE.empty: INTENT.noop,
            STATE.selected: INTENT.upload,
            STATE.current: INTENT.noop,
            STATE.update: INTENT.upload,
            STATE.clear: INTENT.clear,
        }[state]

    def _process(self, old_state, upload, clear):
        new_state = self._decide_new_state(old_state, upload, clear)
        data_update = {
            'state': new_state,
        }

        def wrong_state():
            raise ValueError("Invalid state transition: {} to {}".format(old_state, new_state))

        if old_state == STATE.empty:
            if new_state == STATE.selected:
                data_update['upload'] = upload
                data_update['clear'] = False
            elif new_state == STATE.empty:
                data_update['upload'] = None
                data_update['clear'] = False
            else:
                wrong_state()
        if old_state == STATE.selected:
            if new_state == STATE.selected and upload:
                data_update['upload'] = upload
                data_update['clear'] = False
            if new_state == STATE.selected and not upload:
                # data_update['upload']
                data_update['clear'] = False
            elif new_state == STATE.empty:
                data_update['upload'] = None
                data_update['clear'] = False
            else:
                wrong_state()
        if old_state == STATE.current:
            if new_state == STATE.current:
                data_update['upload'] = None
                data_update['clear'] = False
            elif new_state == STATE.update:
                data_update['upload'] = upload
                data_update['clear'] = False
            elif new_state == STATE.clear:
                data_update['upload'] = None
                data_update['clear'] = True
            else:
                wrong_state()
        if old_state == STATE.update:
            if new_state == STATE.update and upload:
                data_update['upload'] = upload
                data_update['clear'] = False
            elif new_state == STATE.update and not upload:
                # data_update['upload']
                data_update['clear'] = False
            elif new_state == STATE.clear:
                data_update['upload'] = None
                data_update['clear'] = True
            else:
                wrong_state()
        if old_state == STATE.clear:
            if new_state == STATE.clear:
                data_update['upload'] = None
                data_update['clear'] = True
            elif new_state == STATE.update:
                data_update['upload'] = None
                data_update['clear'] = False
            elif new_state == STATE.current:
                data_update['upload'] = None
                data_update['clear'] = False
            else:
                wrong_state()
        data = self.update_data(data_update)
        return new_state, data

    @property
    def field_name(self):
        return self._field_name

    @field_name.setter
    def field_name(self, value):
        if self._field_name is not None:
            if self._field_name != value:
                raise ValueError("Changed field_name?!")
        self._field_name = value

    @property
    def clear_checkbox_name(self):
        return self.field_name + '-clear'

    @property
    def clear_checkbox_id(self):
        return self.clear_checkbox_name + '_id'

    @property
    def cache_input_name(self):
        return self.field_name + '-cache_key'

    @staticmethod
    def is_initial(value):
        """
        Return whether value is considered to be initial value.
        :param value: value for render
        """
        return bool(value) and hasattr(value, 'url')

    def value_from_datadict(self, data, files, name):
        # prep some values:
        self.field_name = name
        self.cache_key = data.get(self.cache_input_name, self.random_key())

        # submitted file:
        upload = super(NormalizedFileInput, self).value_from_datadict(
                data, files, name)
        # value of "Clear" checkbox:
        clear = data.get(self.clear_checkbox_name, False)

        # if we have cached value, return that:
        # @TODO cache the value?  If enter here more then once per request...

        # get persistent data from cache:
        persistent_data = self.get_data()

        # determine the next state and update persistent data
        if not self.new_state:
            self.new_state, persistent_data = self._process(persistent_data['state'], upload, clear)

        # finally, return what is intended:
        intent = self._intent(self.new_state)
        if intent == INTENT.noop:
            return None
        if intent == INTENT.clear:
            return False
        if intent == INTENT.upload:
            if upload:
                return upload
            if persistent_data['upload']:
                return persistent_data['upload']
            raise Exception('Invalid intent-data combination!')

    @staticmethod
    def random_key():
        return uuid.uuid4().hex

    def render(self, name, value, attrs=None):
        self.field_name = name

        # make sure we have a cache key:
        if not self.cache_key:
            self.cache_key = self.random_key()

        # safe initial value to persistent data:
        if self.is_initial(value):
            self.update_data({
                'state': STATE.current,
                'initial_url': value.url,
                'initial_name': value.name,
            })

        # get persistent data:
        persistent_data = self.get_data()

        # construct template for the new state:
        # noinspection PyProtectedMember
        template = self.template.format(
            state=STATE._name(persistent_data['state']),
            state_template=self.state_templates[persistent_data['state']],
            cache_input=HiddenInput().render(
                    self.cache_input_name, self.cache_key, attrs={}),
        )
        template = template.format(**self.template_parts)


        # prepare template substitutions:
        # noinspection PyDictCreation
        substitutions = {
            # input wraps:
            'file_wrap': self.inputs_wraps['file'],
            'clear_wrap': self.inputs_wraps['clear'],
            # texts:
            'text_clear': self.text_clear,
            'text_change': self.text_change,
            'text_initial': self.text_initial,
            'text_temporary': self.text_temporary,
        }
        # ... the file input:
        substitutions['file_input'] = super(NormalizedFileInput, self).render(name, value, attrs)
        # ... "Clear" checkbox:
        if persistent_data['state'] != STATE.empty:  # all other states have the "Clear" checkbox:
            substitutions['clear_checkbox_id'] = conditional_escape(self.clear_checkbox_id)
            substitutions['clear_checkbox'] = CheckboxInput().render(
                    self.clear_checkbox_name,
                    value=persistent_data['clear'],
                    attrs={'id': self.clear_checkbox_id},
            )
        # ... initial file
        if persistent_data['state'] in {STATE.current, STATE.clear}:
            substitutions['initial_url'] = persistent_data['initial_url']
            substitutions['initial_link_text'] = basename(persistent_data['initial_name'])
        # ... temporary file
        if persistent_data['state'] in {STATE.selected, STATE.update}:
            substitutions['temporary_filename'] = basename(persistent_data['upload'].name)

        # fill template variables:
        output = template
        while True:
            new_output = output.format(**substitutions)
            if new_output == output:
                break
            output = new_output
        return mark_safe(output)


class VerboseHTMLMixin(object):
    inputs_wraps = {
        'file':
            '<span class="normalized_fielfield_field_wrap">'
            '{file_input}'
            '</span>',
        'clear':
            '<span class="normalized_fielfield_clear_wrap">'
            '{clear_checkbox}'
            '<label for="{clear_checkbox_id}" class="normalized_fielfield_clear_text">'
            '{text_clear}'
            '</label>'
            '</span>',
    }
    template_parts = {
        'input': '{file_wrap}',
        'change': '<span class="normalized_fielfield_change_wrap">'
                  '<span class="normalized_fielfield_change_text">'
                  '{text_change}'
                  '</span>'
                  '{file_input}'
                  '</span>',
        'initial': '<span class="normalized_fielfield_initial_wrap">'
                   '<span class="normalized_fielfield_initial_text">'
                   '{text_initial}'
                   '</span>'
                   '<a href="{initial_url}" class="normalized_fielfield_initial_link">'
                   '{initial_link_text}'
                   '</a>'
                   '{clear_wrap}'
                   '</span>',
        'temporary': '<span class="normalized_fielfield_temporary_wrap">'
                     '<span class="normalized_fielfield_temporary_text">'
                     '{text_temporary}'
                     '</span>'
                     '<span class="normalized_fielfield_temporary_filename">'
                     '{temporary_filename}'
                     '</span>'
                     '{clear_wrap}'
                     '</span>',
    }
    template = ('<span class="normalized_fielfield normalized_fielfield_state_{state}">'
                '{state_template}{cache_input}</span>')