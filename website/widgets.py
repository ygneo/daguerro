from django import forms
from django.conf import settings
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from mptt.forms import TreeNodeMultipleChoiceField


class TreeCheckboxSelectMultipleWidget(CheckboxSelectMultiple):
    level_indicator = u'-'
    remove_level_indicator = True

    def __init__(self, *args, **kwargs):
        super(TreeCheckboxSelectMultipleWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs):
        output = "<ul>"
        depth = i =  0
        for choice in self.choices:
            choice_id, choice_name = choice[0], choice[1]
            choice_level = self._get_level(choice_name)
            choice_name = self._clean_choice_name(choice_name)
            if choice_level < depth:
                for i in range(0, (depth - choice_level)):
                    output += "</li></ul>"
            elif choice_level > depth:
                output += '<ul>'
            choice_dom_id = "%s%s" % (name, i)
            output += """<li>
                          <input type="checkbox" name="%s" value="%s" id="%s"/>
                          <label for="%s">%s</label>
                      """  % (name, choice_id, choice_dom_id, choice_dom_id, choice_name)
            if depth > 0 and choice_level == depth:
                output += "</li>"
            depth = choice_level 
            i += 1
        output += "</ul>" 
        return mark_safe(output)

    def _get_level(self, choice_name):
        level = 0
        for char in choice_name:
            if char == self.level_indicator:
                level += 1
            else:
                return level
        return level    
            

    def _clean_choice_name(self, choice_name):
        return choice_name.lstrip(self.level_indicator)
        
