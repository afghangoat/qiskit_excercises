from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
#from qiskit.circuit.library import YGate, UnitaryGate
#from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.circuit.classical import expr

backend_name="ibm_brisbane"
service=QiskitRuntimeService()

import matplotlib.pyplot as plt

##Long-range CNOT gate teleportation using dynamic circuits
def dynamic_CNOT_circuit(num_qubit):
    """
    - Assume an 1D chain of nearest neightbors
    - 0th qubit is the control, and last qubit (n-1) is the target
    - The control qubit starts in the + state
    
    """
    num_ancilla=num_qubit-2
    num_ancilla_pair=int(num_ancilla/2)
    qr=QuantumRegister(num_qubit)
    cr1= ClassicalRegister(num_ancilla_pair,name="cr1") #Parity controlled X gate
    cr2=ClassicalRegister(num_ancilla-num_ancilla_pair,name="cr2") #Parity controlled Z gate
    cr3=ClassicalRegister(2,name="cr3") #For final measurements of the control and target qubits
    
    qc=QuantumCircuit(qr,cr1,cr2,cr3)
    
    #Initialize the control qubit
    qc.h(0)
    qc.barrier()
    
    #Entangle the control cubit and the first ancilla qubit
    qc.cx(0,1)
    
    #Create Bell pairs on ancilla qubits
    #from i=1
    for i in range(num_ancilla_pair):
        qc.h(2+2*i)
        qc.cx(2+2*i,2+2*i+1)
        
    #Prepare bell pairs on staggered ancilla and data qubits
    for i in range(num_ancilla_pair+1):
        qc.cx(1+2*i,2+2*i)
    
    for i in range(1,num_ancilla_pair+2):
        qc.h(2*i-1)
    
    #Measurement on alternating ancilla qubits starting with the 1. one
    #Keep track of the parity for the eventual conditional Z gate
    for i in range(1,num_ancilla_pair+2):
        qc.measure(2*i-1,cr2[i-1]) #store data
        if i==1:
            parity_control = expr.lift(cr2[i-1])
        else:
            parity_control = expr.bit_xor(cr2[i-1],parity_control)
    
    #Measurement on staggered alternating ancilla qubits starting with the 2. one
    #Keep track of the parity of the eventualconditional X gate
    for i in range(num_ancilla_pair):
        qc.measure(2*i+2,cr1[i])
        if i==0:
            parity_target=expr.lift(cr1[i])
        else:
            parity_target=expr.bit_xor(cr1[i],parity_target)
    
    with qc.if_test(parity_control):
        qc.z(0) #Control
        
    with qc.if_test(parity_target):
        qc.x(-1) #Target
        
    return qc

#Test
qc=dynamic_CNOT_circuit(num_qubit=7)
#qc.draw(output='mpl')
#plt.show()

max_num_of_qubits=41

qc_list=[]
num_qubit_list=list(range(7,max_num_of_qubits+1,2))

for num_qubit in num_qubit_list:
    qc_list.append(dynamic_CNOT_circuit(num_qubit))
    
'''
#Step 2: Optimize the problem for hardware
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

backend=service.backend(backend_name)

pm=generate_preset_pass_manager(optimization_level=1,backend=backend)

qc_transpiled_list=pm.run(qc_list)

#Step 3: Execute on backend
from qiskit_ibm_runtime import SamplerV2 as Sampler

sampler=Sampler(backend)
job=sampler.run(qc_transpiled_list)
print("Job id: "+str(job.job_id()))
'''
#Step 4: Plot data
job_id="cy55d8n9b62g008hh5bg"
job=service.job(job_id)
result=job.result()

list_Bell = []
list_other=[]
for i in range(0,len(qc_list)-1):
    data=result[i+1].data
    counts = data.cr3.get_counts()
    total_counts=data.cr3.num_shots
    
    prob_Bell=(counts['00']+counts['11']) / total_counts #

    
    list_Bell.append(prob_Bell)
    list_other.append(1-prob_Bell)

plt.plot(num_qubit_list,list_Bell,'--o',label='00 or 11')
plt.plot(num_qubit_list,list_other, '-.^', lobal='other')
plt.xlabel('Number of qubits')
plt.ylabel('Probability')
plt.legend()
#plt.show()