from __future__ import division, print_function, absolute_import

import unittest
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_, assert_array_equal #here posible problem
from scipy.sparse import csr_matrix


def _check_csr_rowslice(i, sl, X, Xcsr):
    np_slice = X[i, sl]
    csr_slice = Xcsr[i, sl]
    assert_array_almost_equal(np_slice, csr_slice.toarray()[0])
    assert_(type(csr_slice) is csr_matrix)


def test_csr_rowslice():
    N = 10
    np.random.seed(0)
    X = np.random.random((N, N))
    X[X > 0.7] = 0
    Xcsr = csr_matrix(X)

    slices = [slice(None, None, None),
              slice(None, None, -1),
              slice(1, -2, 2),
              slice(-2, 1, -2)]

    for i in range(N):
        for sl in slices:
            _check_csr_rowslice(i, sl, X, Xcsr)


def test_csr_getrow():
    N = 10
    np.random.seed(0)
    X = np.random.random((N, N))
    X[X > 0.7] = 0
    Xcsr = csr_matrix(X)

    for i in range(N):
        arr_row = X[i:i + 1, :]
        csr_row = Xcsr.getrow(i)

        assert_array_almost_equal(arr_row, csr_row.toarray())
        assert_(type(csr_row) is csr_matrix)


def test_csr_getcol():
    N = 10
    np.random.seed(0)
    X = np.random.random((N, N))
    X[X > 0.7] = 0
    Xcsr = csr_matrix(X)

    for i in range(N):
        arr_col = X[:, i:i + 1]
        csr_col = Xcsr.getcol(i)

        assert_array_almost_equal(arr_col, csr_col.toarray())
        assert_(type(csr_col) is csr_matrix)


class TestRoundCSR(unittest.TestCase):

    def test_round_csr(self):
        """Tests the __round__ method for csr_matrix."""
        # 1. Setup: Crear una matriz CSR con datos flotantes
        #    Usamos valores específicos para predecir el redondeo fácilmente
        data = np.array([1.23, 4.56, 7.89, -1.11, 0.49, 9.5])
        indices = np.array([0, 2, 1, 3, 0, 3]) # Column indices
        indptr = np.array([0, 2, 3, 4, 6])  # Pointers for rows
        shape = (4, 5) # 4 rows, 5 columns
        A = csr_matrix((data, indices, indptr), shape=shape)
        # Matriz A (aproximada):
        # [[ 1.23, 0.  , 4.56, 0.  , 0.   ],
        #  [ 0.  , 7.89, 0.  , 0.  , 0.   ],
        #  [ 0.  , 0.  , 0.  , -1.11, 0.   ],
        #  [ 0.49, 0.  , 0.  , 9.5 , 0.   ]]

        # --- TDD Fase ROJA: Ejecutar esto ANTES de aplicar el parche ---
        # Se espera que falle con TypeError en la línea `round(A)` o `round(A, 1)`

        # 2. Action: Llamar a round() sobre la matriz
        try:
            rounded_A_0 = round(A)  # Redondeo a 0 decimales (entero más cercano)
            rounded_A_1 = round(A, 1) # Redondeo a 1 decimal
        except TypeError as e:
            # Si estamos en la fase ROJA (antes del parche), este error es ESPERADO.
            # Podemos hacer que el test falle aquí O dejar que la excepción se propague.
            # Para la prueba TDD, simplemente ejecutarlo y ver el TypeError es suficiente.
            # En una suite de tests final, podríamos querer manejar esto de forma diferente
            # si el objetivo fuera probar la ausencia del método, pero aquí queremos
            # probar la funcionalidad *después* del parche.
            # Por ahora, dejaremos que falle si ocurre el TypeError ANTES del parche.
            # Si el parche ya está aplicado, esto no debería lanzar TypeError.
            pass # Opcional: podríamos fallar el test aquí si queremos ser estrictos
                 # con la fase roja: self.fail(f"round(A) lanzó TypeError inesperado: {e}")
                 # Pero es más simple dejar que la excepción detenga el test.


        # 3. Assertion: Verificar el resultado (esto se ejecutará DESPUÉS de aplicar el parche)
        #    Esperado para round(A) (ndigits=0)
        expected_data_0 = np.array([1.0, 5.0, 8.0, -1.0, 0.0, 10.0]) # round([1.23, 4.56, 7.89, -1.11, 0.49, 9.5])
        expected_rounded_A_0 = csr_matrix((expected_data_0, indices, indptr), shape=shape)

        #    Esperado para round(A, 1)
        expected_data_1 = np.array([1.2, 4.6, 7.9, -1.1, 0.5, 9.5]) # round([1.23, 4.56, 7.89, -1.11, 0.49, 9.5], 1)
        expected_rounded_A_1 = csr_matrix((expected_data_1, indices, indptr), shape=shape)

        # Verificaciones usando métodos de unittest y numpy.testing
        # Comprobar que el resultado es una csr_matrix
        self.assertIsInstance(rounded_A_0, csr_matrix, "round(A) no devolvió csr_matrix")  #error
        self.assertIsInstance(rounded_A_1, csr_matrix, "round(A, 1) no devolvió csr_matrix")

        # Comprobar que la estructura (shape, indices, indptr) no ha cambiado
        self.assertEqual(rounded_A_0.shape, A.shape, "Shape cambió después de round(A)")
        assert_array_equal(rounded_A_0.indices, A.indices, "Indices cambiaron después de round(A)")
        assert_array_equal(rounded_A_0.indptr, A.indptr, "Indptr cambió después de round(A)")

        self.assertEqual(rounded_A_1.shape, A.shape, "Shape cambió después de round(A, 1)")
        assert_array_equal(rounded_A_1.indices, A.indices, "Indices cambiaron después de round(A, 1)")
        assert_array_equal(rounded_A_1.indptr, A.indptr, "Indptr cambió después de round(A, 1)")

        # Comprobar que los datos (atributo .data) se han redondeado correctamente
        # Usar assert_array_almost_equal para comparar arrays de floats
        assert_array_almost_equal(rounded_A_0.data, expected_data_0,
                                  err_msg="Los datos no se redondearon correctamente para round(A)")
        assert_array_almost_equal(rounded_A_1.data, expected_data_1,
                                  err_msg="Los datos no se redondearon correctamente para round(A, 1)")

        # Nota: No usamos self.assertAlmostEqual directamente en las matrices,
        # porque unittest no sabe cómo comparar matrices dispersas "casi iguales".
        # Verificar los datos numéricos con numpy.testing es más robusto aquí.

# Puedes añadir más métodos de test (def test_...) a esta clase si es necesario
# por ejemplo, probar con matrices vacías, solo enteros, etc.
