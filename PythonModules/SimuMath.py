'''SimuMath module includes math functions useful for simulations'''


## Licensing
'''
This file is part of SFDEsim.

SFDEsim is free software: you can redistribute it and/or modify it under the terms of the
 GNU General Public License as published by the Free Software Foundation, either version 3
   of the License, or (at your option) any later version.

SFDEsim is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
 even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with SFDEsim. 
If not, see <https://www.gnu.org/licenses/>.
'''

import numpy as np

def rk4_kx(A, B, state, time, input_functions):
    '''Subfunction for RK4 step, calculates the k value'''
    f = []
    for func in input_functions:
        f.append(func(time))
    f = np.array(f,dtype=float)
    return A.dot(f - B.dot(state))


def rk4_step(A, B, state_vector, simulation_time:float, steptime:float, input_functions):
    '''rk4_step is used to integrate discrete difference function step using Runge-Kutta 4 method'''
    k1 = rk4_kx(A, B, state_vector,
                simulation_time, input_functions)
    k2 = rk4_kx(A, B, state_vector+0.5*k1*steptime,
                simulation_time+0.5*steptime, input_functions)
    k3 = rk4_kx(A, B, state_vector+0.5*k2*steptime,
                simulation_time+0.5*steptime, input_functions)
    k4 = rk4_kx(A, B, state_vector+k3*steptime,
                simulation_time*steptime, input_functions)
    return steptime * ((k1 + 2*k2 + 2*k3 + k4)/6)


def cart2pol(x, y):
    '''Returns value of given cartesian coordinates in polar system.\n
       Angle in radians'''
    V = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    return (V, theta)

def pol2cart(V, theta):
    '''Returns value of given polar coordinates in cartesian system.\n
       Angle in radians'''
    x = V * np.cos(theta)
    y = V * np.sin(theta)
    return (x, y)

def angle_loop(theta):
    '''Returns angle of current rotation excluding angle previous rotations.\n
        Angle in degrees'''
    if theta > 360:
        return theta-360
    return theta

def angle_loop_rad(theta):
    '''Returns angle of current rotation excluding angle previous rotations.\n
        Angle in degrees'''
    if theta > 2*np.pi:
        return theta-2*np.pi
    return theta

def pseudoinv(matrix):
    '''Returns pseudo inverse of 2D matrix'''
    for i, row in enumerate(matrix):
        for j, col in enumerate(row):
            if col != 0:
                matrix[i,j] = 1/col
    return matrix


def sign(number):
    '''Returns 1 if input >= 0 otherwise return -1'''
    if number >= 0:
        return 1
    return -1


def complex_euclidian_length(vectors_list):
    '''Computes euclidean length of list of complex numbers'''
    x = 0
    for vect in vectors_list:
        x += (np.sqrt(np.real(vect)**2+np.imag(vect)**2))**2
    return np.sqrt(x)


def solve_power_flow_GS(Y_bus:np.array ,slack_bus:int ,U_vector:np.array,
                        S_vector:np.array, target_error_percentage:float,
                        max_iter_n:int=1000):
    '''Solves bus voltages in multi-bus electrical system using Gauss-Seidel iterator.
       Return list of bus voltages if found, otherwise returs same sized array of NaN.
       Inputs for Y-bus matrix, S-vector and U-vector as np.arrays with dtype=complex.
       Y_bus: Admittance matrix
       slack_bus: bus number of the slack bus, note: first bus is number 1
       U_vector: voltage vector, slack bus has known voltage, other indexes populated with
       iteration starting voltages
       S_vector: apparent powers of busses given as complex numbers, slack bus given as 0
       target_error_percentage: maximum total percentage error of voltages, note: 1% = 1
       max_iter_n: maximum allowed number of iteration cycles, if system does not converge
       within this limit, returns NaN vector'''
    slack_bus = slack_bus-1
    n_bus = len(U_vector)
    U_delta_vect = np.array(np.zeros((n_bus-1,)),dtype=complex)
    for iter_i in range(1,max_iter_n+1):
        U_vector = np.vstack([U_vector,np.zeros((n_bus,))])
        U_vector[iter_i][slack_bus] = U_vector[0][slack_bus]
        for i in range(0,n_bus):
            if i == slack_bus:
                continue
            U_vector[iter_i][i] = ((np.real(S_vector[i])-1j*np.imag(S_vector[i]))/
                                                    np.conjugate(U_vector[iter_i-1][i]))
            for k in range(0,n_bus):
                if k == i:
                    continue
                if k < i:
                    U_vector[iter_i][i] -= Y_bus[i][k]*U_vector[iter_i][k]
                else:
                    U_vector[iter_i][i] -= Y_bus[i][k]*U_vector[iter_i-1][k]
            U_vector[iter_i][i] *= (1/Y_bus[i][i])

        k = 0
        for i, val in enumerate(U_vector[iter_i]):
            if i == slack_bus:
                continue
            U_delta_vect[k] = val-U_vector[iter_i-1][i]
            k += 1

        err = complex_euclidian_length(U_delta_vect)/complex_euclidian_length(U_vector[iter_i])
        if err*100 < target_error_percentage:
            return U_vector[iter_i]

    return np.array([float('nan')]*n_bus)



def solve_2bus_NR(Y_bus:np.array ,U_vector:np.array, S_vector:np.array,
                  target_error_percentage:float, max_iter_n:int=1000):
    '''Solves receiving end voltage of single line using Newton-Raphson method, when
       sending end voltage is known.
       Return the sending end voltage if found, otherwise returs NaN.
       Inputs for Y-bus matrix, S-vector and U-vector as np.arrays with dtype=complex.
       Y_bus: Admittance matrix
       U_vector: voltage vector, sending end voltage in index=0, index=1 has the starting
       iteration starting voltage for receiviing end
       S_vector: apparent powers of receiving end as complex number, sending end as 0
       target_error_percentage: maximum total percentage error of voltages, note: 1% = 1
       max_iter_n: maximum allowed number of iteration cycles, if system does not converge
       within this limit, returns NaN'''
    target_P = target_error_percentage*0.01*np.real(S_vector[1])
    target_Q = target_error_percentage*0.01*np.imag(S_vector[1])

    for i in range(0,max_iter_n):
        print("---iteation---", i)
        delta_angle_1 = 0
        delta_angle_2 = cart2pol(np.real(U_vector[1]),np.imag(U_vector[1]))[1]

        theta_angle21 = cart2pol(np.real(Y_bus[1][0]),np.imag(Y_bus[1][0]))[1]

        theta_angle22 = cart2pol(np.real(Y_bus[1][1]),np.imag(Y_bus[1][1]))[1]

        P2 = (np.abs(U_vector[1])*np.abs(Y_bus[1][0])*np.abs(U_vector[0])*
            np.cos(delta_angle_2-delta_angle_1-theta_angle21)+
            np.abs(U_vector[1])*np.abs(Y_bus[1][1])*np.abs(U_vector[1])*
            np.cos(delta_angle_2-delta_angle_2-theta_angle22))

        Q2 = (np.abs(U_vector[1])*np.abs(Y_bus[1][0])*np.abs(U_vector[0])*
            np.sin(delta_angle_2-delta_angle_1-theta_angle21)+
            np.abs(U_vector[1])*np.abs(Y_bus[1][1])*np.abs(U_vector[1])*
            np.sin(delta_angle_2-delta_angle_2-theta_angle22))

        delta_P = np.real(S_vector[1])-P2
        delta_Q = np.imag(S_vector[1])-Q2

        if np.abs(delta_P) <= np.abs(target_P):
            if np.abs(delta_Q) <= np.abs(target_Q):
                return U_vector[1]

        doh_P2_angle = (-np.abs(U_vector[1])*np.abs(Y_bus[1][0])*np.abs(U_vector[0])*
                        np.sin(delta_angle_2-delta_angle_1-theta_angle21))
        doh_P2_U = (np.abs(U_vector[1])*np.abs(Y_bus[1][1])*np.cos(theta_angle22)+
                    np.abs(Y_bus[1][0])*np.abs(U_vector[0])*np.cos(delta_angle_2-delta_angle_1-theta_angle21)+
                    np.abs(Y_bus[1][1])*np.abs(U_vector[1])*np.cos(delta_angle_2-delta_angle_2-theta_angle22))

        doh_Q2_angle = (np.abs(U_vector[1])*np.abs(Y_bus[1][0])*np.abs(U_vector[0])*
                        np.cos(delta_angle_2-delta_angle_1-theta_angle21))
        doh_Q2_U = (-np.abs(U_vector[1])*np.abs(Y_bus[1][1])*np.sin(theta_angle22)+
                    np.abs(Y_bus[1][0])*np.abs(U_vector[0])*np.sin(delta_angle_2-delta_angle_1-theta_angle21)+
                    np.abs(Y_bus[1][1])*np.abs(U_vector[1])*np.sin(delta_angle_2-delta_angle_2-theta_angle22))


        Jacobian = np.array([[doh_P2_angle,doh_P2_U],
                            [doh_Q2_angle,doh_Q2_U]])
        inv_jacobian = np.linalg.inv(Jacobian)

        delta_vector = np.dot(inv_jacobian,np.array([[delta_P],[delta_Q]]))

        new_U2 = np.abs(U_vector[1])+(delta_vector[1])
        new_delta_angle2 = delta_angle_2+delta_vector[0]
        U = pol2cart(new_U2,new_delta_angle2)

        U_vector[1] = U[0][0]+U[1][0]*1j

    return float('nan')


root_3 = np.sqrt(3)
alpha_beta_matrix = np.array([[1, -0.5, -0.5],
                              [0, root_3/2, -root_3/2],
                              [0.5, 0.5, 0.5]])
inv_alpha_beta_matrix = np.array([[1, 0, 1],
                                  [-0.5, root_3/2, 1],
                                  [-0.5, -root_3/2, 1]])


# Transformations for separately given floats

def abc_to_alpha_beta(a, b, c):
    """Transform from abc to alpha beta, input and output as separate float"""
    alpha = (2*a-b-c)/3
    beta = (b-c)/root_3
    return [alpha, beta]


def alpha_beta_theta_to_dq(alpha, beta, theta):
    """Transform from alpha beta to dq, input and output as separate float"""
    cos_i = np.cos(theta)
    sin_i = np.sin(theta)
    d = alpha*cos_i + beta*sin_i
    q = beta*cos_i - alpha*sin_i
    return [d, q]


def abc_to_dq(a,b,c):
    """Transform from abc to dq, input and output as separate float"""
    alpha_beta = abc_to_alpha_beta(a,b,c)
    return alpha_beta_theta_to_dq(alpha_beta[0],alpha_beta[1], 
                                  np.arctan2(alpha_beta[1],alpha_beta[0]))


def alpha_beta_to_abc(alpha, beta):
    """Transform from alpha beta to abc, input and output as separate float"""
    b = (root_3*beta-alpha)*0.5
    c = (root_3*beta+alpha)*(-0.5)
    return [alpha, b, c]


def dq_to_alpha_beta(d, q, theta):
    """Transform from dq to alpha beta, input and output as separate float"""
    cos_i = np.cos(theta)
    sin_i = np.sin(theta)
    alpha = d*cos_i - q*sin_i
    beta = q*cos_i + d*sin_i
    return [alpha, beta]


def dq_to_abc(d, q, theta):
    """Transform from dq to abc, input and output as separate float"""
    alpha_beta = dq_to_alpha_beta(d,q,theta)
    return alpha_beta_to_abc(alpha_beta[0],alpha_beta[1])


# Transformations for numpy arrays

def np_abc_to_alpha_beta(abc):
    """Transform from abc to alpha beta, input and output as np.array"""
    alpha_beta = np.dot(((2/3)*alpha_beta_matrix), abc)
    return alpha_beta[0:2]


def np_alpha_beta_to_dq(alpha_beta, theta):
    """Transform from alpha beta to dq, input and output as np.array"""
    dq_matrix = np.array([[np.cos(theta), np.sin(theta)],
                         [-np.sin(theta), np.cos(theta)]])
    dq = np.dot(dq_matrix,alpha_beta)
    return dq


def np_abc_to_dq(abc):
    """Transform from abc to dq, input and output as np.array"""
    alpha_beta = np_abc_to_alpha_beta(abc)
    return np_alpha_beta_to_dq(alpha_beta, np.arctan2(alpha_beta[1],alpha_beta[0]))


def np_alpha_beta_to_abc(alpha_beta):
    """Transform from alpha beta to abc, input and output as np.array"""
    return np.dot(inv_alpha_beta_matrix, alpha_beta)


def np_dq_to_alpha_beta(dq, theta):
    """Transform from dq to alpha beta, input and output as np.array"""
    inv_dq_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                              [np.sin(theta), np.cos(theta)]])
    return np.dot(inv_dq_matrix, dq)


def np_dq_to_abc(dq, theta):
    """Trasform from dq to abc, input and output as np.array"""
    return(np_alpha_beta_to_abc(np_dq_to_alpha_beta(dq,theta)))
