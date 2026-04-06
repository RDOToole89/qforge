# Glossary Audit Plan

**Created:** 2026-04-03
**Status:** Infrastructure ready (FurtherReading type + keyEquation field added), content audit pending

## What's Done

- `FurtherReading` interface added to `types.ts` with `title`, `url`, `type`, `note` fields
- `keyEquation` and `formulaExplanation` optional fields added to `GlossaryTerm`
- 15 new terms in "Reconfiguration Space" category with equations and explanations
- Structured decoherence terms updated with equations

## What Needs Doing

### Phase 1: Add `furtherReading` to all ~100+ terms

For each term, add 1-3 links from these source types:

| Type | Source Priority | Example |
|------|----------------|---------|
| `textbook` | Nielsen & Chuang, Preskill lecture notes, Wilde's QIT | Standard references the field relies on |
| `paper` | arXiv papers, foundational papers (Zurek 2003, Berry 1984) | Original results |
| `lecture` | MIT OCW, Preskill's Caltech notes, Scott Aaronson | Free, high-quality explanations |
| `interactive` | Quirk, IBM Quantum Composer, Qiskit tutorials | Hands-on learning |
| `wiki` | Wikipedia (only for well-maintained physics articles) | Quick reference |

### Key References Per Category

**Fundamentals:**
- Nielsen & Chuang "Quantum Computation and Quantum Information" (the bible)
- Preskill lecture notes: http://theory.caltech.edu/~preskill/ph219/
- Scott Aaronson "Quantum Computing Since Democritus"

**Decoherence & Open Systems:**
- Zurek, "Decoherence, einselection, and the quantum origins of the classical" (Rev. Mod. Phys. 75, 715, 2003)
- Schlosshauer, "Decoherence and the Quantum-to-Classical Transition" (textbook)
- Breuer & Petruccione, "The Theory of Open Quantum Systems" (textbook)

**Entanglement:**
- Horodecki et al., "Quantum entanglement" (Rev. Mod. Phys. 81, 865, 2009)
- Bell, "On the Einstein Podolsky Rosen Paradox" (Physics 1, 195, 1964)

**Noise & Channels:**
- Wilde, "Quantum Information Theory" (Cambridge, free on arXiv)
- Lidar & Brun, "Quantum Error Correction" (Cambridge)

**Geometric Phase / Fiber Bundles:**
- Berry, "Quantal Phase Factors Accompanying Adiabatic Changes" (Proc. R. Soc. A 392, 45, 1984)
- Shapere & Wilczek, "Geometric Phases in Physics" (collected papers)

**Constructor Theory:**
- Deutsch & Marletto, "Constructor Theory of Information" (Proc. R. Soc. A 471, 2015)
- Marletto, "The Science of Can and Can't" (popular book)
- Deutsch, "Constructor Theory" (Synthese 190, 4331, 2013)

**Reconfiguration Space (our work):**
- Links to our own docs/research-docs/ as primary source
- Zurek 2003 for einselection foundation
- Berry 1984 for geometric phase foundation

### Phase 2: Add `keyEquation` to all terms that have one

Many terms in fundamentals, gates, linear-algebra already have natural equations that should be formalized.

### Phase 3: Glossary UI enhancements

- Render `keyEquation` with a LaTeX-like formatter (MathJax or react-native-mathjax)
- Render `furtherReading` as clickable links grouped by type
- Add search across all terms
- Add "random term" button for study mode

## Estimated Effort

- Phase 1 (references): 2-3 hours of research + data entry
- Phase 2 (equations): 1-2 hours
- Phase 3 (UI): 1 day
