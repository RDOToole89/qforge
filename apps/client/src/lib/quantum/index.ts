/**
 * Pure, framework-free quantum math (no `three`, no `react`).
 *
 * Single source of truth for the client's quantum mechanics: complex
 * arithmetic, gate matrices + circuit simulation, reduced density matrices /
 * Bloch vectors / correlators, and entanglement measures.
 *
 * Conventions used everywhere in this module:
 *   - A complex number is a `[real, imaginary]` tuple.
 *   - A state vector is `Complex[]` of length 2^n.
 *   - Qubit 0 is the MSB (leftmost bitstring char): the basis-index bit for
 *     qubit q is `1 << (n-1-q)`. This matches the backend
 *     `src/engine/bloch_math.py` partial-trace ordering, so per-qubit indices
 *     line up between the frontend and backend (pinned by the golden fixtures
 *     in `__tests__/golden`).
 */

// Complex arithmetic
export { type Complex, cmul, cadd, cabs2 } from "./complex";

// Gate matrices, application, circuit simulation, and state recognition
export {
  type Mat2,
  I2,
  H_MAT,
  X_MAT,
  Y_MAT,
  Z_MAT,
  S_MAT,
  T_MAT,
  rxMat,
  ryMat,
  rzMat,
  getGateMatrix,
  applySingleQubit,
  applyCNOT,
  applyCZ,
  applySWAP,
  applyToffoli,
  simulateCircuit,
  formatDirac,
  recognizeState,
} from "./gates";

// Reduced density matrices, Bloch vectors, purity, Z-basis correlators
export {
  stateVectorToBloch,
  reducedDensityMatrix1Q,
  purity,
  expectZ,
  expectZZ,
  correlationMatrix,
} from "./density";

// Entanglement measures
export {
  pairConcurrence,
  oneTangle,
  threeTangle,
  multipartiteTangle,
} from "./entanglement";
