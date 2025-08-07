# 🔍 **Dead Code Audit - Clean Architecture v2.0**

## **🎯 OBJECTIVE**

Systematically audit all 71 Python files to identify and remove dead code, ensuring ONLY actively used files remain.

---

## **📋 FOLDER-BY-FOLDER AUDIT**

### **🖥️ src/cli/ - POTENTIAL DUPLICATION**

```
src/cli/
├── __init__.py        # 395B - Exports CLI components
├── commands.py        # 5.1KB - Click-based CLI commands
├── display.py         # 6.1KB - Rich terminal output
├── interactive.py     # 6.6KB - Interactive CLI logic
└── main.py           # 1.2KB - OLD CLI entry point
```

**⚠️ ISSUE**: We have `src/cli/main.py` AND top-level `main.py`

- Current entry: `/main.py` (8.6KB, working)
- Legacy CLI: `src/cli/main.py` (1.2KB, unused?)

**❓ AUDIT QUESTIONS**:

- Is `src/cli/main.py` still used by current `main.py`?
- Are `commands.py`, `display.py`, `interactive.py` actually imported?
- Can we delete the entire `src/cli/` if not used?

### **⚙️ src/config/ - NEEDS REVIEW**

```
src/config/
├── __init__.py        # Exports settings and constants
├── constants.py       # Framework constants
├── params.py         # Parameter validation
└── settings.py       # Centralized settings
```

**✅ STATUS**: Likely needed, but verify all files are imported

### **🧠 src/core/ - MIXED STATUS**

```
src/core/
├── analysis/         # ✅ Used by research pipeline
├── experiment_runner.py  # ✅ Core functionality
├── noise_models/     # ✅ Quantum noise
├── parameter_sweep.py     # ✅ New sweep engine
├── research_handler.py    # ✅ Research analysis
└── state_preparation/     # ✅ Quantum states
```

**✅ STATUS**: Core modules - likely all needed

### **🧪 src/experiments/ - POTENTIAL BLOAT**

```
src/experiments/
├── components/       # ✅ New composable architecture
├── manager.py        # ✅ Experiment manager
├── plugins/          # ❓ Placeholder only?
├── presets/          # ⚠️ POTENTIAL BLOAT
├── validator.py      # ❓ Used or replaced by components/validators.py?
└── __init__.py
```

**⚠️ PRESETS AUDIT NEEDED**:

```
src/experiments/presets/
├── advanced.py       # ❓ How many experiments? Used?
├── beginner.py       # ❓ Basic experiments still needed?
├── ghz_structured_decoherence.py  # ✅ Your research
├── intermediate.py   # ❓ Used?
└── research.py       # ✅ Research experiments
```

### **🧰 src/utils/ - MESS ALERT**

```
src/utils/
├── __init__.py
├── cli.py           # ❓ Argument parsing - duplicate with src/cli/?
├── config_loader.py # ❓ Duplicate with src/config/settings.py?
├── input_handler.py # ❓ User input - still used?
├── logger.py        # ✅ Logging utilities
├── messages.py      # ❓ Internationalization - overkill?
└── results.py       # ❓ Results management - used?
```

**🚨 UTILS PROBLEMS**:

- Likely overlap with `src/cli/` and `src/config/`
- May contain old interaction patterns
- Need to verify what's actually imported

### **📊 src/visualization/ - STATUS UNKNOWN**

```
src/visualization/
├── density_matrix.py
├── histogram.py
├── hypergraph.py         # ❓ Your original research viz
├── visualization_handler.py
├── visualizer.py
└── __init__.py
```

**❓ QUESTIONS**: Are all visualization modules used or just legacy?

### **🧪 src/tests/ - LIKELY STALE**

**⚠️ ISSUE**: Tests probably broken after architecture changes

---

## **✅ COMPLETED CLEANUP**

### **REMOVED DEAD FILES**

- ❌ `src/cli/main.py` - Unused old entry point
- ❌ `src/cli/commands.py` - Only imported by unused main.py
- ❌ `src/utils/cli.py` - Unused argument parsing
- ❌ `src/utils/config_loader.py` - Unused configuration loading
- ❌ `src/utils/results.py` - Unused results management

### **FIXED IMPORTS**

- ✅ Updated `src/cli/__init__.py` to remove dead imports
- ✅ Updated `src/utils/__init__.py` to remove dead imports

### **BROKEN FUNCTIONALITY IDENTIFIED**

- 🚨 **CLI Parameter Collection**: Missing implementation in `src/cli/interactive.py`
- 🚨 **Plotting Questions**: Missing visualization prompts
- ✅ **Available Fix**: Use existing `InputHandler` from `src/utils/input_handler.py`

---

## **🔧 AUDIT METHODOLOGY**

### **Step 1: Import Analysis**

For each folder, check what's actually imported:

```bash
# Find all imports from a specific module
grep -r "from src.cli" src/
grep -r "import.*cli" src/
```

### **Step 2: Entry Point Tracing**

Start from `main.py` and trace what's actually used:

```bash
# Trace imports from main entry point
python3 -c "import main; print('Entry works')"
```

### **Step 3: Dead Code Detection**

```bash
# Find unused Python files
grep -r "import.*filename" src/ || echo "UNUSED"
```

---

## **🎯 CLEANUP PRIORITIES**

### **HIGH PRIORITY**

1. **CLI Duplication** - Resolve `main.py` vs `src/cli/main.py`
2. **Utils Mess** - Remove duplicate functionality
3. **Presets Bloat** - Keep only used experiments

### **MEDIUM PRIORITY**

1. **Tests** - Fix or remove broken tests
2. **Validation** - Remove duplicate validators
3. **Visualization** - Verify what's used

### **LOW PRIORITY**

1. **Documentation** - Update after cleanup
2. **Examples** - Create new examples for clean architecture

---

## **✅ SUCCESS CRITERIA**

- [ ] No duplicate functionality between folders
- [ ] All files in codebase are actively imported/used
- [ ] CLI is clean and configurable
- [ ] Utils folder is minimal and focused
- [ ] Presets contain only necessary experiments
- [ ] Framework still passes all functionality tests
