import qiskit
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import Estimator
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime import EstimatorOptions

import matplotlib.pyplot as plt

backend_name="ibm_brisbane"
service=QiskitRuntimeService()

'''from qiskit_ibm_runtime import QiskitRuntimeService

print("Qiskit version: "+qiskit.__version__)
print("---")

#instantiate service
service = QiskitRuntimeService(channel="ibm_quantum", # ibm_cloud 
token = '***')

#save account
#QiskitRuntimeService.save_account(channel='ibm_quantum',
#token = '***')

backend = service.backend(name = "ibm_brisbane")
print("Num of qubits: "+str(backend.num_qubits))'''

#hello world example by mapping to qubits: on 2 qubit bell state
'''qc = QuantumCircuit(2)

qc.h(0)
qc.cx(0,1)
#map the problem to operators

ZZ=Pauli('ZZ')
ZI=Pauli('ZI')
IZ=Pauli('IZ')
XX=Pauli('XX')
XI=Pauli('XI')
IX=Pauli('IX')
observables=[ZZ,ZI,IZ,XX,XI,IX]

#Optimize circuit observables:
#TODO

#Execute on backend:
estimator=Estimator()

#multiply q circuits, same number as observables
job=estimator.run([qc]*len(observables),observables)

print(job.result())
Plotting a post processing
data=['ZZ','ZI','IZ','XX','XI','IX']
values=job.result().values

plt.plot(data,values,'-o')
plt.xlabel('Observables')
plt.ylabel('Expectation values')

#qc.draw(output='mpl')
plt.show()'''

#Extend hello world to n-qubit GHZ state

#map the problem to circuits and ops
def get_qc_for_n_qubit(n):
    qc=QuantumCircuit(n) #n q-regs
    qc.h(0)
    for i in range(0,n-1):
        qc.cx(i,i+1) #cx=not gate
    return qc

n=100

qc=get_qc_for_n_qubit(n)

operator_strings=['Z'+'I' * i + 'Z' + 'I'* (n-2-i) for i in range(n-1)]
#stats
#print(operator_strings)
#print(len(operator_strings))

operators=[SparsePauliOp(operator_string) for operator_string in operator_strings]

#Optimize the problem for Q execution:
'''
backend=QiskitRuntimeService().backend(backend_name)
pass_manager=generate_preset_pass_manager(optimization_level=1,backend=backend)

qc_transpiled=pass_manager.run(qc)
operators_transpiled_list=[op.apply_layout(qc_transpiled.layout) for op in operators]

#Execute on the backend

options=EstimatorOptions()
options.resilience_level=1 #level 2: zero noise extrapolation
#options.optimization_level=0
options.dynamical_decoupling.enable=True
options.dynamical_decoupling.sequence_type="XY4"

estimator2 = EstimatorV2(backend,options=options)
job2=estimator2.run([(qc_transpiled,operators_transpiled_list)])
job2_id=job2.job_id()

print("Job id: https://quantum.ibm.com/jobs/"+str(job2_id))
'''

#Post processing and plotting

job_retrieving="cy0hq1wnrmz0008536gg"
job=service.job(job_retrieving)

data= list(range(1,len(operators)+1))#X=dist between Z operators
result=job.result()[0]
values=result.data.evs #get expectation values
values= [v/values[0] for v in values]

plt.scatter(data,values,marker='o', label='100 qubit GHZ state')
plt.xlabel('Distance between qubits $i$')
plt.ylabel(r'\langle Z_0 Z_i \rangle / \langle Z_0 Z_i \rangle$')

#qc.draw(output='mpl')
plt.legend()
plt.show()