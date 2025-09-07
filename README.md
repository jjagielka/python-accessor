# Accessor: read nested dictionaries

Build accessor functions using the natural python dot notation.

# Installation

``python-accessor`` is available as a zero-dependency Python package. Install with:

    $ pip install python-accessor


## Usage

```python

    from accessor import accessor as _

    name = _.users.name 
    name(obj)  # equivalent of obj['users']['name']
```

## Examples

```python

from accessor import accessor as _

obj = {
    'users': [{
        'uid': 1234,
        'name': {
            'first': 'John',
            'last': 'Smith',
        }
    }, {
        'uid': 2345,
        'name': {
            'last': 'Bono'
        }
    }, {
        'uid': 3456
    }]
}

_.users[1].name(obj)
# -> {'last': 'Bono'}

_.users.name.last(obj)
# -> ['Smith', 'Bono', None]

_.users.name.first(obj)
# -> ['John', None, None]

_.users.name.first[:1](obj)
# -> ['John']

_.users.uid[:2](obj)
# -> [1234, 2345]

list(map(_.name.last, obj['users']))
# -> ['Smith', 'Bono', None]

list(filter(_.uid > 300, obj['users']))
# -> [{'uid': 3456}]
```

## More Examples! :)

```python

from accessor import accessor as _, select, values

# extract values
list(map(values(_.name.first, _.name.last), obj['users']))
# -> [('John', 'Smith'), (None, 'Bono'), (None, None)]

# extract as dicts
list(map(select(_.name.first, _.name.last),obj['users']))
# -> [{'first': 'John', 'last': 'Smith'}, {'first': None, 'last': 'Bono'}, {'first': None, 'last': None}]

# extract and optionally rename
list(map(select(_.name.uid, x=_.name.last),obj['users']))
# -> [{'uid': '1234', 'x': 'Smith'}, {'uid': 2345, 'x': 'Bono'}, {'uid': 3456, 'x': None}]

```
