from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class UserRegistrationForm(forms.Form):
	username = forms.CharField(
						label='Username', 
						max_length=100, 
						min_length=5,
						widget=forms.TextInput(attrs={'class':'form-control'})
						)
	email = forms.EmailField(
						widget=forms.TextInput(attrs={'class':'form-control'})
						)
	password1 = forms.CharField(
						label='Password', 
						max_length=100, 
						min_length=5,
						widget=forms.PasswordInput(attrs={'class':'form-control'})
						)
	password2 = forms.CharField(
						label='Confirm Password', 
						max_length=100, 
						min_length=5,
						widget=forms.PasswordInput(attrs={'class':'form-control'})
						)

	def clean_email(self):

		email = self.cleaned_data['email']
		qs =  User.objects.filter(email=email)
		if qs.exists():
			raise ValidationError(
    		_('%(value)s'),
    		code='invalid',
    		params={'value': 'Email already exists'},
			)
		return email


	# Doesn't work for some reason, maybe it's because it's not running on an form field just form
	def clean(self):
		cleaned_data = super().clean()
		p1 = cleaned_data.get('password1')
		p2 = cleaned_data.get('password2')
		if p1 and p2:
			if p1 != p2:
				raise ValidationError(
				_('%(value)s'),
				code='invalid',
				params={'value': 'Passwords don\'t match!'},
				)





