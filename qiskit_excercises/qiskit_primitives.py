import qiskit
from qiskit import QuantumCircuit
from qiskit.circuit.library import YGate, UnitaryGate
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService

import numpy as np
import matplotlib.pyplot as plt

backend_name="ibm_brisbane"
service=QiskitRuntimeService()

SYGate = UnitaryGate(YGate().power(1/2),label=r"$\sqrt{Y}$")
SYdgGate = UnitaryGate(SYGate.inverse(),label=r"$\sqrt{Y}^\dag$")

#Transverse field icing model to demo primitives

#Generate 1 dim. transverse field
def generate_1d_tfim_circuit(num_qubity,num_trotter_steps,rx_angle, num_classical_bits=0,trotter_barriers=False,layer_barriers=False):
    
    if num_classical_bits==0:
        qc = QuantumCircuit(num_qubity)
    else:
        qc = QuantumCircuit(num_qubity,num_classical_bits)
    
    for trotter_step in range(num_trotter_steps):
        add_1d_tfim_trotter_layer(qc,rx_angle,layer_barriers)
        if trotter_barriers==True:
            qc.barrier() #add barrier
        
    return qc
    
def add_1d_tfim_trotter_layer(qc, rx_angle,layer_barriers=False):
    
    #Adding Rzz gates in the even layers
    for i in range(0,qc.num_qubits-1,2):
        qc.sdg([i,i+1]) #Sdagger
        qc.append(SYGate, [i+1])
        qc.cx(i,i+1)
        qc.append(SYdgGate, [i+1])
    
    if layer_barriers==True:
        qc.barrier()
        
    #Odd ones
    for i in range(1,qc.num_qubits-1,2):
        qc.sdg([i,i+1]) #Sdagger
        qc.append(SYGate, [i+1])
        qc.cx(i,i+1) #cnot
        qc.append(SYdgGate, [i+1])
    
    if layer_barriers==True:
        qc.barrier()
    
    qc.rx(rx_angle, list(range(qc.num_qubits)))
    
    if layer_barriers==True:
        qc.barrier()

#Test
'''num_qubits=6
num_trotter_steps=1
rx_angle=0.5*np.pi

qc=generate_1d_tfim_circuit(num_qubits,num_trotter_steps,rx_angle,True,True)'''

#Sampler demo

#Generate mirrored 1 dim. transverse field
def append_mirrored_1d_tfim_circuit(qc, num_qubity,num_trotter_steps,rx_angle, trotter_barriers=False,layer_barriers=False):
    
    for trotter_step in range(num_trotter_steps):
        add_mirrored_1d_tfim_trotter_layer(qc,rx_angle,layer_barriers)
        if trotter_barriers==True:
            qc.barrier() #add barrier
        
    return qc
    
def add_mirrored_1d_tfim_trotter_layer(qc, rx_angle,layer_barriers=False):
    
    #Invert it *-1
    qc.rx(-rx_angle, list(range(qc.num_qubits)))
    
    if layer_barriers==True:
        qc.barrier()
    
    #Odd ones
    for i in range(1,qc.num_qubits-1,2):
        #Gates inverted
        qc.append(SYGate, [i+1])
        qc.cx(i,i+1) #cnot, that one stays
        qc.append(SYdgGate, [i+1])
        qc.s([i,i+1]) #Sdagger inverse
        
    if layer_barriers==True:
        qc.barrier()
        
    #Adding Rzz gates in the even layers
    for i in range(0,qc.num_qubits-1,2):
        #Gates inverted
        qc.append(SYGate, [i+1])
        qc.cx(i,i+1) #cnot, that one stays
        qc.append(SYdgGate, [i+1])
        qc.s([i,i+1]) #Sdagger inverse
    
    if layer_barriers==True:
        qc.barrier()
        
#Test mirrored
#append_mirrored_1d_tfim_circuit(qc,num_qubits,num_trotter_steps,rx_angle,True,True)

#qc.draw(output='mpl',fold=-1)
#plt.show()

#Create circuits and observables
num_trotter_steps=1
max_trotter_steps=10

num_qubits=100;

rx_angle=0.5*np.pi

#measure survivability of the bitstring between middle qubits
measured_qubits= [49,50]
'''
qc_list=[]
for trotter_step in range(max_trotter_steps):
    qc=generate_1d_tfim_circuit(num_qubits,num_trotter_steps,rx_angle,len(measured_qubits),True,True)
    append_mirrored_1d_tfim_circuit(qc,num_qubits,num_trotter_steps,rx_angle,True,True)
    qc.measure(measured_qubits,list(range(len(measured_qubits)))) #Or for 2 measureds just [0,1]
    qc_list.append(qc)
'''
#Step 2: Optimize
backend=service.backend(backend_name)
print("Done instantiating the backend!...")

'''qc_transpiled_list=transpile(qc_list, backend=backend,optimization_level=1)

#Step 3: Execute on hardware
from qiskit_ibm_runtime import SamplerV2 as Sampler
#from qiskit_ibm_runtime.options.sampler_options import SamplerOptions

sampler=Sampler(backend)
sampler.options.dynamical_decoupling.enable=True
sampler.options.dynamical_decoupling.sequence_type="XY4"

job=sampler.run(qc_transpiled_list)
print("Job id: "+ str(job.job_id()))'''

#Step 4: Post-process and plot the data
'''job_id= "cy54b95cw2k0008jscsg"

#get survival probability of all 0 bitstring
job = service.job(job_id)

survival_probability_list=[]
for trotter_step in range(max_trotter_steps):
    try:
        data=job.result()[trotter_step].data
        survival_probability_list.append(data.c.get_counts()['0'*len(measured_qubits)] /data.c.num_shots)
    except:
        survival_probability_list.append(0) #nothing survived

plt.plot(list(range(0,4*max_trotter_steps,4)),survival_probability_list, '--o')
plt.xlabel('2Qbit gate depth')
plt.ylabel('Survival probability of the all-0 bitstring')
plt.xticks(np.arange(0,44,4))'''

#Or draw circuits:
#qc_list[1].draw(output='mpl',fold=-1)

#plt.show()

#Estimator

#Step 1: map the problem
from qiskit.circuit import Parameter
rx_angle = Parameter("rx_angle")

qc=generate_1d_tfim_circuit(num_qubits,2,rx_angle)

#measure magnetization
from qiskit.quantum_info import SparsePauliOp

middle_index=num_qubits//2
observable=SparsePauliOp("I"*middle_index+"Z"+"I"*(middle_index-1))

#Step 2: Optimize
qc_transpiled=transpile(qc,backend=backend,optimization_level=1)
observable=observable.apply_layout(qc_transpiled.layout)

#Step 3: Execute on quantum hardware
'''from qiskit_ibm_runtime import EstimatorV2, EstimatorOptions

min_rx_angle=0
max_rx_angle=np.pi/2
num_rx_angle=12

trotter_steps=2

rx_angle_list=np.linspace(min_rx_angle,max_rx_angle,num_rx_angle)

options=EstimatorOptions()
options.resilience_level=1

options.dynamical_decoupling.enable=True
options.dynamical_decoupling.sequence_type="XY4"

estimator=EstimatorV2(backend,options=options)

job = estimator.run([(qc_transpiled,observable,rx_angle_list)])
print("Job id: "+str(job.job_id))
'''
#Step 4: mapping and plotting the data
job_id="cy54mxb01rbg008j3pq0"
job2=service.job(job_id)

exp_val_list.job.result()[0].data.evs

plt.plot(rx_angle_list/np.pi,exp_val_list,'--o')
plt.xlabel(r'Rx angle ($\pi$)')
plt.ylabel(r'$\langle Z \rangle in the middle of the chain')

plt.ylim(-0.1,1.1)
plt.show()

