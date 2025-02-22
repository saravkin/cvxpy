"""
Copyright 2013 Steven Diamond

This file is part of CVXPY.

CVXPY is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CVXPY is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CVXPY.  If not, see <http://www.gnu.org/licenses/>.
"""

from cvxpy.atoms import affine_prod, quad_form, quad_over_lin, matrix_frac, sum_squares, norm, max_entries
from cvxpy.atoms.affine.vstack import vstack
from cvxpy.atoms.elementwise.power import power
from cvxpy.expressions.expression import *
from cvxpy.expressions.variables import Variable
from cvxpy import Problem, Minimize
import unittest
from cvxpy.tests.base_test import BaseTest
import numpy as np
import warnings

class TestExpressions(BaseTest):
    """ Unit tests for the expression/expression module. """
    def setUp(self):
        pass

    # Test elementwise power
    def test_power(self):
        x = Variable(3)
        y = Variable(3)
        self.assertFalse(x.is_constant())
        self.assertTrue(x.is_affine())
        self.assertTrue(x.is_quadratic())

        s = power(x.T*y, 0)
        self.assertTrue(s.is_constant())
        self.assertTrue(s.is_affine())
        self.assertTrue(s.is_quadratic())

        t = power(x-y, 1)
        self.assertFalse(t.is_constant())
        self.assertTrue(t.is_affine())
        self.assertTrue(t.is_quadratic())

        u = power(x+2*y, 2)
        self.assertFalse(u.is_constant())
        self.assertFalse(u.is_affine())
        self.assertTrue(u.is_quadratic())
        self.assertTrue(u.is_dcp())

        w = (x+2*y)**2
        self.assertFalse(w.is_constant())
        self.assertFalse(w.is_affine())
        self.assertTrue(w.is_quadratic())
        self.assertTrue(w.is_dcp())
    
    def test_matrix_multiplication(self):
        x = Variable(3, 5)
        y = Variable(3, 5)
        self.assertFalse(x.is_constant())
        self.assertTrue(x.is_affine())
        self.assertTrue(x.is_quadratic())

        s = x.T*y
        self.assertFalse(s.is_constant())
        self.assertFalse(s.is_affine())
        self.assertTrue(s.is_quadratic())
        self.assertFalse(s.is_dcp())
    
    def test_quad_over_lin(self):
        x = Variable(3, 5)
        y = Variable(3, 5)
        z = Variable()
        s = quad_over_lin(x-y, z)
        self.assertFalse(s.is_constant())
        self.assertFalse(s.is_affine())
        self.assertFalse(s.is_quadratic())
        self.assertTrue(s.is_dcp())
        
        t = quad_over_lin(x+2*y, 5)
        self.assertFalse(t.is_constant())
        self.assertFalse(t.is_affine())
        self.assertTrue(t.is_quadratic())
        self.assertTrue(t.is_dcp())
    
    def test_matrix_frac(self):
        x = Variable(5)
        M = np.asmatrix(np.random.randn(5, 5))
        P = M.T*M
        s = matrix_frac(x, P)
        self.assertFalse(s.is_constant())
        self.assertFalse(s.is_affine())
        self.assertTrue(s.is_quadratic())
        self.assertTrue(s.is_dcp())
    
    def test_quadratic_form(self):
        x = Variable(5)
        P = np.asmatrix(np.random.randn(5, 5))
        q = np.asmatrix(np.random.randn(5, 1))
        s = x.T*P*x + q.T*x
        self.assertFalse(s.is_constant())
        self.assertFalse(s.is_affine())
        self.assertTrue(s.is_quadratic())
        self.assertFalse(s.is_dcp())

    def test_sum_squares(self):
        X = Variable(5, 4)
        P = np.asmatrix(np.random.randn(3, 5))
        Q = np.asmatrix(np.random.randn(4, 7))
        M = np.asmatrix(np.random.randn(3, 7))
        
        y = P*X*Q + M
        self.assertFalse(y.is_constant())
        self.assertTrue(y.is_affine())
        self.assertTrue(y.is_quadratic())
        self.assertTrue(y.is_dcp())

        s = sum_squares(y)
        self.assertFalse(s.is_constant())
        self.assertFalse(s.is_affine())
        self.assertTrue(s.is_quadratic())
        self.assertTrue(s.is_dcp())

        # Frobenius norm squared is indeed quadratic
        # but can't show quadraticity using recursive rules
        t = norm(y, 'fro')**2
        self.assertFalse(t.is_constant())
        self.assertFalse(t.is_affine())
        self.assertFalse(t.is_quadratic())
        self.assertTrue(t.is_dcp())

    def test_indefinite_quadratic(self):
        x = Variable()
        y = Variable()
        z = Variable()

        s = y*z
        self.assertTrue(s.is_quadratic())
        self.assertFalse(s.is_dcp())

        t = (x+y)**2 - s - z*z
        self.assertTrue(t.is_quadratic())
        self.assertFalse(t.is_dcp())

    def test_non_quadratic(self):
        x = Variable()
        y = Variable()
        z = Variable()
        with self.assertRaises(Exception) as cm:
            (x*y*z).is_quadratic()
        self.assertEqual(str(cm.exception), "Cannot multiply UNKNOWN and AFFINE.")

        s = max_entries(vstack(x, y, z))**2
        self.assertFalse(s.is_quadratic())
        
        t = max_entries(vstack(x**2, power(y, 2), z))
        self.assertFalse(t.is_quadratic())

    def test_affine_prod(self):
        x = Variable(3, 5)
        y = Variable(5, 4)

        s = affine_prod(x, y)
        self.assertFalse(s.is_constant())
        self.assertFalse(s.is_affine())
        self.assertTrue(s.is_quadratic())
        self.assertFalse(s.is_dcp())
