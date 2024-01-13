# IMPORTING LIBRARIES
# Standard library imports
from datetime import datetime
from typing import Any
import json

# Related third-party imports
from django import forms
from django.core.validators import EmailValidator, MinLengthValidator, MaxLengthValidator
from django.contrib.auth.password_validation import validate_password

# Form Classes
class ProjectForm(forms.Form):
    projectCode = forms.IntegerField(
        required=True,
        )
    projectType = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=2,
        )
    projectName = forms.CharField(
        max_length=100,
        required=True,
        validators=[
            MinLengthValidator(10), 
            MaxLengthValidator(100)]
        )
    associatedClient = forms.CharField(required=False)
    projectDescription = forms.CharField(
        max_length=250,
        required=True,
        validators=[
            MinLengthValidator(10), 
            MaxLengthValidator(250)
            ]
        )
    projectLeader = forms.CharField(
        max_length=8,
        validators=[MinLengthValidator(5), MaxLengthValidator(8)],
        required=True,
    )
    quotedHours = forms.FloatField(required=True)
    

class TaskForm(forms.Form):
    projectCode = forms.CharField(
        max_length=10,
        validators=[MinLengthValidator(3), MaxLengthValidator(10)],
        required=True,
    )
    taskCodeInput = forms.CharField(
        max_length=10,
        validators=[MinLengthValidator(3), MaxLengthValidator(10)],
        required=True,
    )
    responsable = forms.CharField(
        max_length=8,
        validators=[MinLengthValidator(5), MaxLengthValidator(8)],
        required=True,
    )
    taskName = forms.CharField(
        max_length=100,
        validators=[MinLengthValidator(10), MaxLengthValidator(100)],
        required=True,
    )
    taskDescription = forms.CharField(
        max_length=250,
        validators=[MinLengthValidator(10), MaxLengthValidator(250)],
        required=True,
    )
    planHours = forms.FloatField(required=True)
    taskPriority = forms.IntegerField(required=True)


class UserForm(forms.Form):
    username = forms.CharField(
        max_length=15, validators=[MinLengthValidator(5), MaxLengthValidator(15)]
    )
    password = forms.CharField(validators=[validate_password])
    firstName = forms.CharField(
        max_length=30, validators=[MinLengthValidator(5), MaxLengthValidator(30)]
    )
    lastName = forms.CharField(
        max_length=100, validators=[MinLengthValidator(5), MaxLengthValidator(100)]
    )
    email = forms.EmailField(
        validators=[EmailValidator()]
    )
    privileges = forms.CharField(required=True)
    isActive = forms.CharField(required=True)
    
    
class ClientForm(forms.Form):
    privileges = forms.CharField(required=True)
    isActive = forms.CharField(required=True)