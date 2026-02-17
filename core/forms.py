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
        fields = ['name', 'icon', 'level', 'description', 'issuing_structure']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ex: Python Débutant'
            }),
            'icon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'level': forms.RadioSelect(),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez les compétences validées par ce badge...'
            }),
            'issuing_structure': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

class StructureForm(forms.ModelForm):
    """
    Form for creating and updating structures
    """
    class Meta:
        model = Structure
        fields = ['name', 'logo', 'type', 'address', 'siret', 'description', 
                 'referent_last_name', 'referent_first_name', 'referent_position',
                 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ex: Association Python France'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse complète de la structure'
            }),
            'siret': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 123 456 789 00012'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description de la structure, ses activités, sa mission...'
            }),
            'referent_last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de famille'
            }),
            'referent_first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'referent_position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Président, Directeur, etc.'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 48.8566',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 2.3522',
                'step': 'any'
            }),
        }

class UserForm(forms.ModelForm):
    """
    Form for creating and updating users profiles
    """
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "avatar", "address"]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Nom de famille'
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Email'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Mot de passe'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Adresse ...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    password_confirm = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirmation du mot de passe'
        }), label='Confirmation du mot de passe')

    def clean(self):
        """Check if password and password_confirm are matching"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password != password_confirm:
            self.add_error(None, 'Les mots de passes ne correspondent pas')

        return cleaned_data


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