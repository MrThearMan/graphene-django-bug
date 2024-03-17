# Graphene Django Bug

This repo demonstrates an incompatibility between 
`graphene-django` 3.2.0 (latest as of writing) and
`django-rest-framework` 3.15.0 (latest as of writing).

## Steps to reproduce

1. Clone this repo.

```shell
git clone https://github.com/MrThearMan/graphene-django-bug.git
```

2. Create a virtual environment and install the requirements.

> This repo is set up with poetry 1.8.2 but can use other tools.

```shell
cd graphene-django-bug
poetry install
```

3. Run the server: `python manage.py runserver` 

```shell
poetry run python manage.py runserver
```

4. Navigate to `http://127.0.0.1:8000/graphql/`. This should result in the following error:


```shell
Internal Server Error: /graphql/
Traceback (most recent call last):
  File ".../site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/django/core/handlers/base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/django/views/generic/base.py", line 97, in view
    self = cls(**initkwargs)
           ^^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene_django/views.py", line 114, in __init__
    schema = graphene_settings.SCHEMA
             ^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene_django/settings.py", line 127, in __getattr__
    val = perform_import(val, attr)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene_django/settings.py", line 66, in perform_import
    return import_from_string(val, setting_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene_django/settings.py", line 80, in import_from_string
    module = importlib.import_module(module_path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1381, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1354, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1325, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 929, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 994, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "...graphene-django-bug/example/schema.py", line 18, in <module>
    class ExampleMutation(SerializerMutation):
  File ".../site-packages/graphene/types/objecttype.py", line 30, in __new__
    base_cls = super().__new__(
               ^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene/utils/subclass_with_meta.py", line 46, in __init_subclass__
    super_class.__init_subclass_with_meta__(**options)
  File ".../site-packages/graphene_django/rest_framework/mutation.py", line 101, in __init_subclass_with_meta__
    input_fields = fields_for_serializer(
                   ^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene_django/rest_framework/mutation.py", line 55, in fields_for_serializer
    fields[name] = convert_serializer_field(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene_django/rest_framework/serializer_converter.py", line 33, in convert_serializer_field
    graphql_type = get_graphene_type_from_serializer_field(field)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../functools.py", line 909, in wrapper
    return dispatch(args[0].__class__)(*args, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene_django/rest_framework/serializer_converter.py", line 168, in convert_serializer_field_to_enum
    return convert_choices_to_named_enum_with_descriptions(name, field.choices)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene_django/converter.py", line 92, in convert_choices_to_named_enum_with_descriptions
    choices = list(get_choices(choices))
              ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/graphene_django/converter.py", line 77, in get_choices
    for value, help_text in choices:
        ^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 2)
```

This error happens when converting choice field choices to enums for serializer mutations fields.
This is due to `django-rest-framework` 3.15.0 changing from [OrderedDicts to regular dicts][drf].
The code in `graphene-django` makes an `isinstance` check against OrderedDicts to change an iterable:

```python
# graphene_django/converter.py, lines 72-78

def get_choices(choices):
    converted_names = []
    if isinstance(choices, OrderedDict):  # <- This is the problem
        return choices.items()
    for value, help_text in choices:  # <- This line fails
        ...
```

Iterating a dict will only return the keys, not the key-value pairs, which is what the code expects.

## Fix

The fix is to change the `isinstance` check to check for `dict` instead of `OrderedDict`.
This shouldn't affect anything, as OrderedDict is a subclass of dict.


[drf]: https://www.django-rest-framework.org/community/release-notes/#315x-series:~:text=Replaced%20OrderedDict%20with%20dict%20%5B%238964%5D
