/**
 * Complex arithmetic for quantum statevector simulation.
 *
 * Pure, framework-free (no `three`, no `react`). This is the single home for
 * complex-number helpers used across the client's quantum math.
 *
 * A complex number is represented as a `[real, imaginary]` tuple, matching the
 * statevector convention used throughout the circuit builder and Bloch sphere.
 */

/** Complex number as [real, imaginary]. */
export type Complex = [number, number];

/** Complex multiplication: (a)(b). */
export function cmul(a: Complex, b: Complex): Complex {
  return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
}

/** Complex addition: a + b. */
export function cadd(a: Complex, b: Complex): Complex {
  return [a[0] + b[0], a[1] + b[1]];
}

/** Squared magnitude |a|^2 = re^2 + im^2. */
export function cabs2(a: Complex): number {
  return a[0] * a[0] + a[1] * a[1];
}
