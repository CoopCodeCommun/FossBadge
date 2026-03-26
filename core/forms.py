from django import forms
from .models import Badge, Structure, User

class BadgeForm(forms.ModelForm):
    """
    Form for creating and updating badges
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["issuing_structure"].queryset = self.request.user.structures


    class Meta:
        model = Badge
        fields = ['name', 'icon', 'description', 'issuing_structure']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ex: Python Débutant'
            }),
            'icon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            # 'level': forms.RadioSelect(),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez les compétences validées par ce badge...'
            }),
            'issuing_structure': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

class PartialUserForm(forms.ModelForm):
    """
    Forms for editing user profiles
    """
    class Meta:
        model = User
        fields = ["first_name","last_name","address"]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Nom de famille'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Adresse ...'
            }),
        }