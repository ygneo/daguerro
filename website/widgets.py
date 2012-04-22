from django import forms
from django.conf import settings
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from mptt.forms import TreeNodeMultipleChoiceField


class TreeCheckboxSelectMultipleWidget(CheckboxSelectMultiple):
    level_indicator = u'-'
    remove_level_indicator = True
    item_template = """<li>
                        <input type="checkbox" name="%(choice_name)s value="%(value)s" id="%(dom_id)s" %(checked)s />
                        <label for="%(name)s">%(name)s</label>
                    """

    def __init__(self, *args, **kwargs):        
        try:
            self.show_empty_choices = kwargs.pop("show_empty_choices")
        except KeyError:
            self.show_empty_choices = True
        super(TreeCheckboxSelectMultipleWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs):
        output = ""
        depth = 0
        for choice in self._cleaned_choices():            
            choice_id, choice_name, choice_level = choice[0], choice[1], choice[2]
            item_output = ""
            if choice_level < depth:
                for i in range(0, (depth - choice_level)):
                    item_output += "</li></ul>"
            elif choice_level > depth:
                item_output += '<ul>'
            choice_dom_id = "%s%s" % (name, choice_id)
            item_output += self.item_template % {'choice_name': choice_name, 'value': choice_id, 
                                                 'name': choice_name, 'dom_id': choice_dom_id,
                                                 'checked': 'checked="checked"'}
            if depth > 0 and choice_level == depth:
                item_output += "</li>"
            depth = choice_level 
            output += item_output
        output = "<ul>%s</ul>" % output
        return mark_safe(output)

    def _get_level(self, choice_name):
        level = 0
        for char in choice_name:
            if char == self.level_indicator:
                level += 1
            else:
                return level
        return level    

    def _cleaned_choices(self):
        for choice in self.choices:
            if self.show_empty_choices or choice[0] != "":
                cleaned_choice = (choice[0],
                                  self._clean_choice_name(choice[1]),
                                  self._get_level(choice[1]))
                yield cleaned_choice

    def _clean_choice_name(self, choice_name):
        return choice_name.lstrip(self.level_indicator)
        
