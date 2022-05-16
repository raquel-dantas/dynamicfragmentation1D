import numpy as np
import itertools
import copy 


# Input for the simulation of the expanding ring as an 1D bar

# Young's module 
E = 275.0*10**9  # (Pa)
# Density
rho = 2750.0  # (kg/m3)

# Lenght of the bar (L)
L = 50*10**-3  # (m)
x0 = -L/2
xf = L/2

# Number of linear elements (n_el)
n_el = 300
# Lenght of each linear element (h)
h = L/n_el

# Critical time step
dt_crit = h/((E/rho)**0.5)
# Adopted time step
dt = dt_crit*0.1  # (s)
# Time integration
time_simulation = 6.0*10**-7 # (s)
# Number of time steps (n_steps)
n_steps = int(time_simulation/dt)
time_simulation = n_steps*dt # (s)
print(dt)
print(n_steps)

# Applied strain rate and veloctities
strain_rate = 10.0**4  # (s-1)
vel = strain_rate*L/2 

# Material id convention: 
# 0 : line elemnt
# 1 : interface element
# 2 : Support left node
# 3 : Support right node 
# 4 : Velocity applied left node
# 5 : Velocity applied right node
materials = [0] * n_el
materials.append(4)
materials.append(5)

# node_id[elem_index][local_node], returns the global node id
node_id = [[i,i+1] for i in range(n_el)]

# Identify each node has apllied BCs
node_id.append([0]) # Applied velocity at left boundary
node_id.append([n_el]) # Applied velocity at right boundary 

# Connect[el][j] returns the global index of local dof 'j' of the element 'el'
connect = copy.deepcopy(node_id) 


# BC dictionary
bc_dict = {
    2: (0, "dirichlet"),
    4: (-vel, "velocity"),
    5: (vel, "velocity")
}
# Number of degree of freedom 
n_dofs = max(list(itertools.chain.from_iterable(connect))) + 1

# Cross sectional area
A = 1*10**-3  # (m2)
# Fracture energy
Gc = 100.0  # (N/m)
# Limit stress
stress_c = 300.0*10**6  # (Pa)
# Limit fracture oppening
delta_c = (2.0*Gc)/stress_c




# Initial values

# Initial displacement (u0)
u0 = np.zeros((n_dofs))
# Initial velocity (v0): velocity profile (vel) is a function v(x)
n_points = n_dofs
l = np.linspace(-L/2, L/2, n_points)
v0 = np.array([strain_rate*x for x in l])
v0 = np.round(v0, 8)
# Initial acceleration (acel0)
acel0 = np.zeros((n_dofs))
# Inital load (p)
p = np.zeros((n_steps+1, n_dofs))
# Damping
C = np.zeros((n_dofs, n_dofs))
# Initialization of maximum jump u between two linear elements (delta_max)
delta_max = np.zeros((len(materials)*2))