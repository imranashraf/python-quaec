..
    This work is licensed under the Creative Commons Attribution-
    NonCommercial-ShareAlike 3.0 Unported License. To view a copy of this
    license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a
    letter to Creative Commons, 444 Castro Street, Suite 900, Mountain View,
    California, 94041, USA.

Pauli and Clifford Groups
=========================

:class:`qecc.Pauli` - Class representing Pauli group elements
-------------------------------------------------------------

.. autoclass:: qecc.Pauli
    :members:
    :undoc-members:

The :class:`qecc.Pauli` class supports multiplication, tensor products and
negation by the ``*``, ``&`` and ``-`` operators, respectively.

>>> P = qecc.Pauli('X')
>>> Q = qecc.Pauli('Y')
>>> P * Q
i^1 Z
>>> P & Q
i^0 XY
>>> -P * Q
i^3 Z

Additionally, instances of :class:`qecc.Pauli` can be tested for equality.

>>> -P * Q == P * -Q
True
>>> P * Q != Q * P
True

The length of a :class:`qecc.Pauli` is defined as the number of qubits it acts
upon.

>>> len(qecc.Pauli('XYZI'))
4

Utility Functions
~~~~~~~~~~~~~~~~~

.. autofunction:: qecc.com

.. autofunction:: qecc.pauli_group

.. autofunction:: qecc.from_generators

.. autofunction:: qecc.is_in_normalizer

.. autofunction:: qecc.elem_gens

.. autofunction:: qecc.eye_p

:class:`qecc.Clifford` - Class representing Clifford group elements
-------------------------------------------------------------------

.. autoclass:: qecc.Clifford
    :members:
    :undoc-members:

Common Clifford Gates
~~~~~~~~~~~~~~~~~~~~~

The :mod:`qecc` package provides support for several common Clifford operators.
These functions can be used to quickly analyze small circuits. For more
extensive circuit support, please see :doc:`circuits`.

.. autofunction:: qecc.eye_c

.. autofunction:: qecc.cnot

.. autofunction:: qecc.hadamard

.. autofunction:: qecc.phase

.. autofunction:: qecc.swap

.. autofunction:: qecc.cz

.. autofunction:: qecc.pauli_gate

Utility Functions
~~~~~~~~~~~~~~~~~

.. autofunction:: qecc.paulify

