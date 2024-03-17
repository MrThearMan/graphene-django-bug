from django.db import models


class ExampleChoice(models.TextChoices):
    FOO = "Foo"
    BAR = "Bar"


class Example(models.Model):
    choice = models.CharField(max_length=3, choices=ExampleChoice.choices)
