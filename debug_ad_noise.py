
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, amplitude_damping_error

def test_ad_noise():
    # 1. Create a simple circuit: |11>
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.x(1)
    qc.measure_all()

    # 2. Create AD noise
    error_rate = 0.5
    ad_1q = amplitude_damping_error(error_rate)
    ad_2q = ad_1q.tensor(ad_1q)

    # 3. Create Noise Model
    noise_model = NoiseModel()
    # Apply to Identity gates (we will add identity gates to the circuit to test)
    # noise_model.add_all_qubit_quantum_error(ad_2q, "id")
    # Actually, let's apply to a custom gate or just X?
    # Let's apply to 'id' and add 'id' to circuit.

    qc_noise = QuantumCircuit(2)
    qc_noise.x(0)
    qc_noise.x(1)
    qc_noise.id(0) # Apply noise here? No, id is 1q.
    # Let's apply to 'barrier' or just use 'delay'?
    # Better: Apply to 'x' gate.
    noise_model.add_all_qubit_quantum_error(ad_1q, "x")

    qc_noise.measure_all()

    # Run
    sim = AerSimulator(noise_model=noise_model)
    t_qc = transpile(qc_noise, sim)
    result = sim.run(t_qc, shots=1000).result()
    counts = result.get_counts()
    print("Single Qubit AD on X gates:")
    print(counts)

    # Test 2-qubit AD on CX
    qc_cx = QuantumCircuit(2)
    qc_cx.x(0) # |10>
    qc_cx.cx(0, 1) # |11>
    qc_cx.measure_all()

    noise_model_cx = NoiseModel()
    noise_model_cx.add_all_qubit_quantum_error(ad_2q, "cx")

    sim_cx = AerSimulator(noise_model=noise_model_cx)
    t_qc_cx = transpile(qc_cx, sim_cx)
    result_cx = sim_cx.run(t_qc_cx, shots=1000).result()
    counts_cx = result_cx.get_counts()
    print("\nTwo Qubit AD on CX gate:")
    print(counts_cx)

if __name__ == "__main__":
    test_ad_noise()
