#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# CliffordClass.py: Implementation of qecc.Clifford and related utility
#     functions.
##
# © 2012 Christopher E. Granade (cgranade@gmail.com) and
#     Ben Criger (bcriger@gmail.com).
# This file is a part of the QuaEC project.
# Licensed under the AGPL version 3.
##
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

## RELAOD FIX ##
# This is a pretty poor way of fixing it, but should work for now.
    
import PauliClass as _pc
import bsf as _bsf

try:
    reload(_pc)
    reload(_bsf)
except:
    # If it fails, we're no worse off, so just ignore the problem.
    pass

## IMPORTS ##

from itertools import product, chain, combinations
from PauliClass import *
from bsf import *
from numpy import hstack, newaxis

## ALL ##

__all__ = [
    'Clifford',
    'eye_c', 'cnot', 'replace_one_character', 'cz', 'hadamard', 'phase', 
    'permutation', 'swap', 'pauli_gate', 'paulify', 'gen_cliff'
]

## CONSTANTS ##

VALID_OPS = ['I', 'X', 'Y', 'Z']
VALID_PHS = range(4)

## CLASSES ##

EmptyClifford = object() # FIXME: We need a better singleton object here.

class Clifford(object):
    r"""
    Class representing an element of the Cifford group on :math:`n` qubits.
    
    :param xbars: A list of operators :math:`\bar{X}_i` such that the
        represented Clifford operation :math:`C` acts as :math:`C(X_i) = \bar{X}_i`.
    :param zbars: See ``xbars``.
    :type xbars: list of :class:`qecc.Pauli` instances
    :type zbars: list of :class:`qecc.Pauli` instances
    """
    
    def __init__(self, xbars, zbars):
        for output_xz in xbars+zbars:
            if not isinstance(output_xz,Pauli):
                raise TypeError("Output operators must be Paulis.")
        self.xout=xbars
        self.zout=zbars

    def __len__(self):
        """

        Yields the number of qubits on which the Clifford ``self`` acts.

        """
        exes=self.xout
        return len(exes[0])

    def __repr__(self):
        """Prints a Clifford in Pauli notation (yielding a list of 
        input Paulis, and a list of output Paulis.)"""
        left_side_x,left_side_z=elem_gens(len(self))
        right_side=self.xout+self.zout
        return '\n'.join(
                '{gen} |-> {out}'.format(gen=gen, out=out)
                for gen, out in zip(left_side_x + left_side_z, self.xout + self.zout)
            )

    def is_valid(self):
        """
        Checks that the output of the represented Clifford gate obeys the proper
        commutation relations.
        """
        for P in sum(elem_gens(len(self)), []):
            for Q in sum(elem_gens(len(self)), []):
                if com(self.conjugate_pauli(P), self.conjugate_pauli(Q)) != com(P, Q):
                    print P, Q, self.conjugate_pauli(P), self.conjugate_pauli(Q)
                    return False
                    
        return True

    def conjugate_pauli(self,pauli):
        r"""

        Given an instance of :class:`qecc.Pauli` representing the operator
        :math:`P`, calculates the mapping :math:`CPC^{\dagger}`.

        :arg pauli: Representation of the Pauli operator :math:`P`.
        :type pauli: qecc.Pauli
        :returns: Representation of the Pauli operator :math:`CPC^{\dagger}`,
            where :math:`C` is the Clifford operator represented by this
            instance.
        :rtype: qecc.Pauli
        """
        
        if not isinstance(pauli,Pauli):
            # If we don't have a Pauli, maybe we have an iterable over Paulis?
            try:

                dummy = iter(pauli)
                # Yep. It was an iterable.
                return map(self.conjugate_pauli, pauli)
            except TypeError:
                # Nope. Wasn't iterable. Raise an error.
                raise TypeError("Cliffords conjugate Paulis.")
        #Initialize the output Pauli to the identity:
        rolling_pauli=Pauli('I'*len(pauli))        
        for idx,op in enumerate(pauli.op):
            #For every X/Z the input Pauli contains, multiply by the corresponding
            #output Pauli from self. 
            if op == 'X':
                rolling_pauli=rolling_pauli*self.xout[idx]
            elif op == 'Z':
                rolling_pauli=rolling_pauli*self.zout[idx]
            elif op == 'Y':
                #Y = iXZ:
                rolling_pauli=rolling_pauli*self.xout[idx]*self.zout[idx]
                rolling_pauli.mul_phase(1)
        return rolling_pauli 

    def __eq__(self,other):
        return (self.xout==other.xout)and(self.zout==other.zout)


    def __mul__(self,other):
        """multiplies two Cliffords, self and other, by conjugating the output Paulis from other,
        according to the relations given by self, yielding self*other. """
        if not isinstance(other,Clifford):
            return NotImplemented 
        Xs=[]
        Zs=[]
        for ex, zed in zip(other.xout,other.zout):
            Xs.append(self.conjugate_pauli(ex))
            Zs.append(self.conjugate_pauli(zed))
        return Clifford(Xs,Zs)

    def __rand__(self, other):
        if other is EmptyClifford:
            return self
            
        return NotImplemented

    def __and__(self,other):
        """Takes the tensor product of two Cliffords *self* and *other*."""
        if other is EmptyClifford:
            return self
            
        if not isinstance(other,Clifford):
            return NotImplemented 
        nq_self=len(self)
        nq_other=len(other)
        id_self_size=eye_p(nq_self)
        id_other_size=eye_p(nq_other)
        #We embed each Clifford into a larger space, and concatenate the output lists.
        exones=[]
        extwos=[]
        zedones=[]
        zedtwos=[]
        for idx in range(nq_self):
            exones.append(self.xout[idx] & id_other_size)
            zedones.append(self.zout[idx] & id_other_size)
        for idx in range(nq_other):
            extwos.append(id_self_size & other.xout[idx])
            zedtwos.append(id_self_size & other.zout[idx])
        return Clifford(exones+extwos,zedones+zedtwos)

    def __call__(self, other):
        if not isinstance(other,Clifford):
            return NotImplemented
        return self.conjugate_pauli(other)

    def as_bsm(self):
        """
        Returns a representation of the Clifford operator as a binary symplectic
        matrix.
        
        :rtype: :class:`qecc.BinarySymplecticMatrix`
        """
        def to_col(P):
            v = P.as_bsv()
            out = hstack([v.x, v.z])[..., newaxis]
            return out
        return BinarySymplecticMatrix(hstack(map(to_col, self.xout + self.zout)))
    
## FUNCTIONS ##
def eye_c(nq):
    """
    Yields the identity Clifford, defined to map every generator of the Pauli group to itself.

    :rtype: Clifford
    """
    return Clifford(*elem_gens(nq)) if nq > 0 else EmptyClifford
    
def replace_one_character(string,location,new_character):
    """
    Replaces the character in ``string`` at ``location`` with ``new_character``.

    :rtype: str
    """
    return string[:location]+new_character+string[location+1:]
    
def cnot(nq,ctrl,targ):
    """
    Yields the ``nq``-qubit CNOT Clifford controlled on ``ctrl``, acting a Pauli :math:`X` on ``targ``.

    :rtype: :class:`qecc.Clifford`
    """
    #Initialize to the identity Clifford:
    cnotto=eye_c(nq)
    #Wherever ctrl has an X, put an X on targ:
    cnotto.xout[ctrl].op=replace_one_character(cnotto.xout[ctrl].op,targ,'X')
    #Wherever targ has a Z, put a Z on ctrl:
    cnotto.zout[targ].op=replace_one_character(cnotto.zout[targ].op,ctrl,'Z')
    return cnotto
    
def cz(nq, q1, q2):
    """
    Yields the ``nq``-qubit C-Z Clifford, acting on qubits ``q1`` and ``q2``.

    :rtype: :class:`qecc.Clifford`
    """
    #Initialize to the identity Clifford:
    gate = eye_c(nq)
    #Wherever ctrl or targ get an X, map to XZ:
    gate.xout[q1].op = replace_one_character(gate.xout[q1].op, q2, 'Z')
    gate.xout[q2].op = replace_one_character(gate.xout[q2].op, q1, 'Z')
    return gate
    
def hadamard(nq,q):
    """
    Yields the ``nq``-qubit Clifford, switching :math:`X` and :math:`Z` on qubit ``q``, yielding a minus sign on :math:`Y`.

    :rtype: :class:`qecc.Clifford`
    """
    #Switch a Z and an X in the identity Clifford:
    return eye_c(q) & Clifford([Pauli('Z')],[Pauli('X')]) & eye_c(nq-q-1)

def phase(nq,q):
    r"""
    Yields the :math:`\frac{\pi}{4}_z`-rotation Clifford, acting on qubit ``q``.

    :rtype: :class:`qecc.Clifford`
    """
    return eye_c(q) & Clifford([Pauli('Y')],[Pauli('Z')]) & eye_c(nq-q-1)
    
def permutation(lst, p):
    """
    Permutes a list ``lst`` according to a set of indices ``p``.

    :rtype: list
    """
    return [lst[idx] for idx in p]
    
def swap(nq, q1, q2):
    """
    Yields the swap Clifford, on ``nq`` qubits, which swaps the Pauli generators on ``q1`` and ``q2``.

    :rtype: :class:`qecc.Clifford`
    """
    p = range(nq)
    p[q1], p[q2] = p[q2], p[q1]
    
    gate = eye_c(nq)
    gate.xout = permutation(gate.xout, p)
    gate.zout = permutation(gate.zout, p)
    return gate
    
def pauli_gate(pauli):
    """
    Imports an instance of the :class:`qecc.Pauli` class into the :class:`qecc.Clifford` class, representing a Pauli as a series of sign changes.

    :rtype: :class:`qecc.Clifford`
    """
    nq = len(pauli.op)
    return Clifford(*tuple(
        [gen.mul_phase(2*com(pauli,gen))  for gen in gen_set]
        for gen_set in elem_gens(nq)
    ))

def paulify(clinput):
    """
    Tests an input Clifford ``clinput`` to determine if it is, in
    fact, a Pauli. If so, it outputs the Pauli. If not, it
    returns the Clifford. 

    BE WARNED: If you turn a Pauli 
    into a Clifford and back again, the phase will be lost.
    """
    
    nq=len(clinput.xout) #Determine number of qubits.
    test_ex,test_zed=elem_gens(nq) #Get paulis to compare.
    """If the Paulis input to the Clifford are only altered in phase, then the Clifford is also a Pauli."""
    for ex_clif,zed_clif,ex_test,zed_test in zip(clinput.xout, clinput.zout,test_ex,test_zed):
        if ex_clif.op != ex_test.op or zed_clif.op != zed_test.op:
            print "Clifford is not Pauli."
            return clinput
        #If the Clifford is Pauli, determine which by examining operators with altered phases.
        exact=eye_p(nq)
        zedact=eye_p(nq) #Initialize accumulators
        """If a negative sign appears on a given generator, assign a Pauli to that qubit that conjugates the generator to a minus sign, e.g. ZXZ = -X """
        for idx_x in range(nq):
            if clinput.xout[idx_x].ph==2:
                exact.op = replace_one_character(exact.op, idx_x, 'Z')
        for idx_z in range(nq):
            if clinput.zout[idx_z].ph==2:
                zedact.op = replace_one_character(zedact.op, idx_z, 'X')
        return Pauli((exact*zedact).op)

def gen_cliff(paulis_in,paulis_out):
    """The canonical form of the Clifford that takes the list paulis_in to the list paulis_out."""
    nq=len(paulis_in)/2
    
    xins=paulis_in[0:nq]
    zins=paulis_in[nq:2*nq]
    
    xouts=paulis_out[0:nq]
    zouts=paulis_out[nq:2*nq]
    
    G    = Clifford(xouts,zouts)
    H    = Clifford(xins,zins)    
    Hinv = (H.as_bsm().inv().as_clifford())
    return G*Hinv
    
