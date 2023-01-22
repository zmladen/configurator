"""
The winding module. It is used to store all the important parametes for the winding.

The :mod:`winding` module contains several classes:

- :class:`wire`
- :class:`coil`
- :class:`winding`

Interitance diagram
*******************

.. inheritance-diagram:: wire coil winding
   :parts: 1
"""

from .coil import coil
from .wire import wire
from .winding import winding
