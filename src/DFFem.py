import numpy as np
import itertools
import DFMesh


def LocalSystem(elem_index):
    """Returns local stifness and mass matrices.
    """
    
    # Size of linear elements
    h = DFMesh.ElemLength(elem_index)
    # Local stifness and mass matrix
    k_elem = DFMesh.E*DFMesh.A/h * np.array([[1.0, -1.0], [-1.0, 1.0]])
    m_elem = DFMesh.rho*DFMesh.A*h/2 * np.array([[1.0, 0.], [0., 1.0]])

    return k_elem, m_elem


def Gl_index(elem_index, local_dof):
    """Returns the global index of a local dof."""

    return DFMesh.connect[elem_index][local_dof]


def Apply_bc(K, M, F, elem_index):
    """Apply boundary conditions.\n
    Arguments:\n
    K -- Global stiffness matrix which will be alterated to take account the contribution;\n
    M -- Global stiffness matrix;\n
    F -- Global load vector.\n"""

    phi = 1.0
    # Penalty number
    bignumber = 10.0**30
    dof = DFMesh.connect[elem_index][0]
    value, bc_type = DFMesh.bc_dict[DFMesh.materials[elem_index]]
    if bc_type == "dirichlet":
        K[dof, dof] += bignumber*phi*phi
        F[dof] += bignumber*float(value)*phi
        M[dof, dof] += float("inf")
    if bc_type == "velocity":
        M[dof, dof] += float("inf")


def Contribute_el(K, M, F, elem_index):
    """Computes the contribution of element in the global stiffness and mass matrices, and load vector.\n
    Arguments:\n
    K -- Global stiffness matrix which will be alterated to take account the contribution;\n
    M -- Global stiffness matrix;\n
    F -- Global load vector."""
    
    # Element load vector
    f_elem = np.array([0.0, 0.0])

    # Contribution to K, M and F
    k_elem, m_elem = LocalSystem(elem_index)
    for i_loc in range(2):
        i_gl = Gl_index(elem_index, i_loc)
        F[i_gl] += f_elem[i_loc]
        for j_loc in range(2):
            j_gl = Gl_index(elem_index, j_loc)
            K[i_gl, j_gl] += k_elem[i_loc, j_loc]
            M[i_gl, j_gl] += m_elem[i_loc, j_loc]


def GlobalSystem():
    """ Returns global stiffness and mass matrices, and global load vector."""

    n_dofs = max(list(itertools.chain.from_iterable(DFMesh.connect))) + 1

    # Initiation of variables 
    K = np.zeros((n_dofs, n_dofs))
    F = np.zeros((n_dofs))
    M = np.zeros((n_dofs, n_dofs))

    # Assembly of elements
    n_el = len(DFMesh.connect)
    for i_el in range(n_el):
        mat_id = DFMesh.materials[i_el]
        if mat_id == 0:
            Contribute_el(K, M, F, i_el)
        elif DFMesh.bc_dict.__contains__(mat_id):
            Apply_bc(K, M, F, i_el)

    return K, M, F