from django import forms
from .models import Badge, Structure

class BadgeForm(forms.ModelForm):
    """
    Form for creating and updating badges
    """
    # Make valid_structures a multiple select field
    valid_structures = forms.ModelMultipleChoiceField(
        queryset=Structure.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Structures où ce badge est valable"
    )

    class Meta:
        model = Badge
        fields = ['name', 'icon', 'level', 'description', 'issuing_structure', 'valid_structures']
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
