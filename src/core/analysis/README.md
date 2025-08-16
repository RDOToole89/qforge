# Analysis Module Documentation

This module contains quantum state analysis algorithms organized by domain.

## Folder Structure

### `/core/` - Fundamental Analysis Functions
Core mathematical and information-theoretic functions that form the foundation of quantum analysis.

- **`information_theory.py`** - Shannon entropy, mutual information, KL divergence, research metrics aggregation
- **`correlations.py`** - Pairwise quantum correlations, adaptive thresholds, hypergraph edge computation  
- **`bloch.py`** - Bloch sphere analysis and visualization utilities

### `/dynamics/` - Time Evolution & Decoherence
Analysis of quantum state evolution, decoherence patterns, and temporal dynamics.

- **`decoherence.py`** - Fubini-Study distance, state evolution metrics
- **`clustering.py`** - Pattern clustering and pathway analysis
- **`transitions.py`** - State transition analysis and error pathway tracking

### `/symmetry/` - Symmetry Analysis
Group theory and symmetry analysis for quantum states.

- **`symmetry.py`** - SU(2)/SU(3) symmetries, parity distributions, group theoretical analysis

### `/structured_decoherence/` - Research-Specific Metrics
**NEW MODULE**: Implements the 5 quantitative metrics for structured decoherence pathway research.

- **`pathway_metrics.py`** - Core implementation of AI, PCR, EEC, TPS, CES metrics
- **`pathway_analysis.py`** - High-level analysis functions combining all metrics
- **`README.md`** - Detailed documentation of research methodology and metric definitions

## Usage Patterns

### For Basic Information Theory
```python
from src.core.analysis.core.information_theory import compute_shannon_entropy
```

### For Structured Decoherence Research  
```python
from src.core.analysis.structured_decoherence import compute_pathway_metrics
```

### For General Research Analysis
```python
from src.core.analysis import compute_research_metrics  # Aggregates all metrics
```