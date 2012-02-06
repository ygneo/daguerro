from django import forms

class ShoppingCartForm(forms.Form):
    pass


class SearchOptionsForm(forms.Form):

    title = forms.BooleanField(required=False, initial=True)
    alternative_title = forms.BooleanField(required=False, initial=True)
    family = forms.BooleanField(required=False, initial=True)
    tags = forms.BooleanField(required=False, initial=True)
    caption = forms.BooleanField(required=False, initial=False)
    location_title = forms.BooleanField(required=False, initial=False)

    # Buscar en 
    # [] Titulo [] Nom cient [] Familia [] Etiquetas
    # [] Pie de foto  [] Localiz
    # Categorias 
    # [] 
    #   []
    
    class Meta:
        fields = ['title', 'alternative_title', 'family',
                  'caption', 'tags', 'location_title', 
                  'galleries']
        fieldsets = [('default-fields',
                      {'fields': ['title', 
                       'alternative_title',
                       'family', 'tags']}),
                     ('advanced-fields',
                      {'fields': ['caption', 
                                  'location_title']}),
                     ('galleries', 
                      {'fields': ['galleries']}),
                     ]
         
                      
    
                          
