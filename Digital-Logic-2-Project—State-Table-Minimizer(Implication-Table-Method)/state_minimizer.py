"""
State Table Minimizer — Implication Table Method
Digital Logic 2 — Project

Supports:
 * (no don't-cares)
 * (don't-cares represented as '-')

The program walks through every step shown in the lecture slides:
  Step 1 — Fill the implication table
  Step 2 — Mark incompatible pairs (output mismatch  → x)
  Step 3 — Propagate (dependency pairs that resolve to x → x)
  Step 4 — Collect compatible / equivalent pairs  (✓)
  Step 5 — Build equivalence classes
  Step 6 — Build the reduced state table
"""

import sys
import copy

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QScrollArea, QMessageBox, QSplitter, QTextEdit,
    QGroupBox, QSpinBox, QLineEdit, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor



#  the CORE


def parse_cell(raw: str):
    """
    Parse a combined 'NextState,Output' cell such as 'A,00' or '-,-'.
    Returns (next_state, output) where either can be None (don't-care).
    """
    raw = raw.strip()
    if ',' in raw:#membership operator
        parts = raw.split(',', 1)#str.split(separator, max_splits)
        ns  = None if parts[0].strip() in ('-', '') else parts[0].strip().upper()#the strip is useless but for some resoans split put ' ' on it's owm
        out = None if parts[1].strip() in ('-', '') else parts[1].strip()#value_if_true if condition else value_if_false
    else:
        # Treat the whole cell as just an output (Moore)
        ns  = None
        out = None if raw in ('-', '') else raw
    return ns, out


def outputs_compatible(o1, o2) -> bool:
    """
    Two outputs are compatible when:
      * at least one is don't-care (None), OR
      * they are equal strings.
    """
    if o1 is None or o2 is None:
        return True
    return o1 == o2


def next_states_pair(ns1, ns2):
    """
    Return the (sorted) pair of next states that must also be compatible,
    or None if either next state is don't-care (no constraint generated).
    """
    if ns1 is None or ns2 is None:
        return None
    a, b = sorted([ns1, ns2])
    if a == b:
        return None
    return (a, b)


class ImplicationTableSolver:
    """
    Runs the full implication-table algorithm and records every sub-step
    so the GUI can replay them one at a time.
    """

    def __init__(self, states, inputs, table):
        """
        states : list of state names, ex. ['A','B','C','D']
        inputs : list of input labels, ex. ['XY=00','XY=01','XY=10','XY=11']
        table  : dict  state → list of (next_state | None, output | None)
                 one entry per input column, in the same order as `inputs`
        """
        self.states = states
        self.inputs = inputs
        self.table  = table          # {state: [(ns,out), ...]}
        self.steps  = []             # list of (description, snapshot)

        # All unordered pairs  (i,j)  with i < j  (lexicographic on states list)
        self.pairs = [
            (self.states[i], self.states[j])
            for i in range(len(self.states))
            for j in range(i + 1, len(self.states))
        ]
        #self.pairs = []

        #for i in range(len(self.states)):
        #    for j in range(i + 1, len(self.states)):
        #        self.pairs.append(
        #             (self.states[i], self.states[j])
        #        )

        # Cell status: 'unknown' | 'X' (incompatible) | 'check' (compatible)
        # deps[pair] = list of pairs that this cell depends on
        self.status = {p: 'unknown' for p in self.pairs}
        self.deps   = {p: []        for p in self.pairs}

        self._solve()#. operator access member of object

    #==================================================
    # helpers

    def _snapshot(self):
        """Deep-copy current status dict for step recording."""
        return copy.deepcopy(self.status)  #from a lib. so this heaven

    def _record(self, description):
        self.steps.append((description, self._snapshot()))

    #===================================================
    # The algorithm

    def _solve(self):
        self._record("Initial empty implication table.")

        # ── STEP 1: output-mismatch pass ─────────────────────────────────────
        changed_step1 = []
        for (p, q) in self.pairs:
            incompatible = False
            dep_pairs    = []

            for idx, inp in enumerate(self.inputs):
                ns_p, out_p = self.table[p][idx]
                ns_q, out_q = self.table[q][idx]

                # Check output compatibility for this input column
                if not outputs_compatible(out_p, out_q):
                    incompatible = True
                    break

                # Collect next-state dependency
                np = next_states_pair(ns_p, ns_q)
                if np and np != (p, q):   # skip self-reference
                    dep_pairs.append((inp, np))

            if incompatible:
                self.status[(p, q)] = 'X'
                changed_step1.append(f"({p},{q})")
            else:
                self.deps[(p, q)] = dep_pairs   # store for propagation

        desc = ("Step 1 — Mark pairs whose outputs differ in at least one "
                "input column with ✗ (directly incompatible).")
        if changed_step1:
            desc += f"\n  Marked ✗: {', '.join(changed_step1)}"
        self._record(desc)

        # ── STEP 2: fill dependency pairs ────────────────────────────────────
        self._record(
            "Step 2 — For remaining cells, record the next-state pairs "
            "that must also be compatible (dependency conditions)."
        )

        # ── STEP 3: iterative propagation ────────────────────────────────────
        iteration = 0
        while True:
            iteration += 1
            newly_marked = []
            for (p, q) in self.pairs:
                if self.status[(p, q)] != 'unknown':
                    continue
                # If any dependency is already marked ✗, this pair becomes ✗
                for (inp, dep) in self.deps[(p, q)]:
                    if self.status[dep] == 'X':
                        self.status[(p, q)] = 'X'
                        newly_marked.append(f"({p},{q}) [dep on {dep} via {inp}]")
                        break

            desc = (f"Step 3 (iteration {iteration}) — Propagation pass: "
                    "mark cells ✗ if any dependency is already ✗.")
            if newly_marked:
                desc += f"\n  Newly marked ✗: {'; '.join(newly_marked)}"
            else:
                desc += "\n  No new marks — propagation complete."
            self._record(desc)

            if not newly_marked:
                break

        # ── STEP 4: remaining unknowns → compatible ───────────────────────────
        compatible_pairs = []
        for (p, q) in self.pairs:
            if self.status[(p, q)] == 'unknown':
                self.status[(p, q)] = 'check'
                compatible_pairs.append(f"({p},{q})")

        desc = ("Step 4 — All remaining unmarked cells are compatible (✓).")
        if compatible_pairs:
            desc += f"\n  Compatible pairs: {', '.join(compatible_pairs)}"
        self._record(desc)

        # ── STEP 5: build equivalence classes (union-find) ───────────────────
        self.equiv_classes = self._build_equiv_classes()
        class_strs = ['{' + ','.join(sorted(c)) + '}' for c in self.equiv_classes]
        self._record(
            "Step 5 — Merge compatible pairs into equivalence classes "
            "(maximal groups of mutually compatible states).\n  "
            + "  ".join(class_strs)
        )

        # ── STEP 6: build reduced table ───────────────────────────────────────
        self.reduced_states, self.reduced_table = self._build_reduced_table()
        self._record(
            "Step 6 — Construct the reduced state table using the "
            "equivalence classes as new states."
        )

    def _build_equiv_classes(self):
        """
        Union-Find to group states: two states are in the same class iff
        their pair is marked compatible (✓).
        For incompletely specified machines we use the maximal compatibles
        approach simplified to: merge all ✓ pairs.
        """
        parent = {s: s for s in self.states}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        for (p, q) in self.pairs:
            if self.status[(p, q)] == 'check':
                union(p, q)

        # Group by root
        groups = {}
        for s in self.states:
            root = find(s)
            groups.setdefault(root, []).append(s)

        # Sort each group and sort groups by their first element
        result = [sorted(g) for g in groups.values()]
        result.sort(key=lambda g: self.states.index(g[0]))
        return result

    def _build_reduced_table(self):
        """
        Assign a new label (X, Y, Z … or α, β …) to each equivalence class,
        then rewrite the state table using the new labels.
        """
        # Map each original state → new label
        new_labels = 'XYZWVUTSRQPONMLKJIHGFEDCBA'
        if len(self.equiv_classes) > len(new_labels):
            new_labels = [f"S{i}" for i in range(len(self.equiv_classes))]

        state_to_new = {}
        label_order  = []
        for idx, cls in enumerate(self.equiv_classes):
            label = new_labels[idx]
            label_order.append(label)
            for s in cls:
                state_to_new[s] = label

        reduced = {}   # new_label -> [(new_ns | '-', out | '-'), ...]
        for cls in self.equiv_classes:
            rep   = cls[0]                      # representative state
            lbl   = state_to_new[rep]
            row   = []
            for idx in range(len(self.inputs)):
                ns_rep, out_rep = self.table[rep][idx]
                new_ns = state_to_new[ns_rep] if ns_rep else '-'
                new_out = out_rep if out_rep else '-'
                row.append((new_ns, new_out))
            reduced[lbl] = row

        return label_order, reduced

    def get_deps_text(self, pair):
        """Return a human-readable string of the dependencies for a pair."""
        parts = []
        for (inp, dep) in self.deps[pair]:
            parts.append(f"{inp}\n({dep[0]},{dep[1]})")
        return '\n'.join(parts) if parts else '✓'


# ─────────────────────────────────────────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────────────────────────────────────────

CELL_SIZE  = 86    # pixels per implication-table cell
HEADER_SZ  = 38

COLOR_X       = '#FF6B6B'   # red   — incompatible
COLOR_CHECK   = '#6BCB77'   # green — compatible
COLOR_DEP     = '#FFD93D'   # yellow — has dependencies
COLOR_UNKNOWN = '#FFFFFF'   # white — not yet decided
COLOR_HEADER  = '#4D96FF'   # blue  — header cells
COLOR_BG      = '#1E1E2E'   # dark background
COLOR_PANEL   = '#2A2A3E'
COLOR_TEXT    = '#CDD6F4'
COLOR_ACCENT  = '#89B4FA'


class ImplicationTableWidget(QWidget):
    """
    Draws the lower-triangular implication table as a grid of labels.
    Rows = states[1..n], Columns = states[0..n-2]
    Cell (row i, col j) shown only when j < i  (pair i,j).
    """

    def __init__(self, states, pairs, parent=None):
        super().__init__(parent)
        self.states   = states
        self.pairs    = pairs
        self.cells    = {}   # (row_state, col_state) → QLabel
        self._build()

    def _build(self):
        n   = len(self.states)
        lay = QGridLayout(self)
        lay.setSpacing(2)

        # Column headers (states[0] … states[n-2])
        for j, s in enumerate(self.states[:-1]):
            lbl = QLabel(s)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(CELL_SIZE, HEADER_SZ)
            lbl.setStyleSheet(
                f"background:{COLOR_HEADER};color:white;"
                "font-weight:bold;border-radius:4px;"
            )
            lay.addWidget(lbl, 0, j + 1)

        # Row headers + cells
        for i in range(1, n):
            row_state = self.states[i]

            # Row header
            rh = QLabel(row_state)
            rh.setAlignment(Qt.AlignCenter)
            rh.setFixedSize(HEADER_SZ, CELL_SIZE)
            rh.setStyleSheet(
                f"background:{COLOR_HEADER};color:white;"
                "font-weight:bold;border-radius:4px;"
            )
            lay.addWidget(rh, i, 0)

            # Cells — only columns j < i
            for j in range(i):
                col_state = self.states[j]
                cell = QLabel('?')
                cell.setAlignment(Qt.AlignCenter)
                cell.setFixedSize(CELL_SIZE, CELL_SIZE)
                cell.setWordWrap(True)
                cell.setStyleSheet(
                    f"background:{COLOR_UNKNOWN};border:1px solid #888;"
                    "border-radius:4px;font-size:11px;color:black;font-weight:bold;"
                )
                lay.addWidget(cell, i, j + 1)
                self.cells[(row_state, col_state)] = cell

        self.setLayout(lay)
        self.adjustSize()

    def update_cells(self, status: dict, solver: ImplicationTableSolver):
        """
        Refresh every cell's colour and text to match the current status dict.
        """
        for (p, q), cell in self.cells.items():
            # Normalize: we store pairs as (smaller_idx, larger_idx)
            key = tuple(sorted([p, q], key=lambda s: solver.states.index(s)))
            st  = status.get(key, 'unknown')

            if st == 'X':
                bg   = COLOR_X
                text = '✗'
            elif st == 'check':
                bg   = COLOR_CHECK
                text = '✓'
            else:
                # Show dependencies if any
                dep_text = solver.get_deps_text(key)
                bg   = COLOR_DEP if dep_text != '✓' else COLOR_UNKNOWN
                text = dep_text if dep_text != '✓' else '?'

            cell.setStyleSheet(
                f"background:{bg};border:1px solid #555;"
                "border-radius:4px;font-size:11px;padding:1px;color:black;font-weight:bold;"
            )
            cell.setText(text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("State Table Minimizer — Implication Table Method")
        self.setMinimumSize(1200, 750)
        self._apply_dark_theme()
        self._build_ui()

        # Pre-load the Q1 example from the lecture slides
        self._load_example_q1()

    # ── theme ─────────────────────────────────────────────────────────────────

    def _apply_dark_theme(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background:{COLOR_BG}; color:{COLOR_TEXT}; }}
            QPushButton {{
                background:{COLOR_ACCENT}; color:#1E1E2E;
                border-radius:6px; padding:6px 14px; font-weight:bold;
            }}
            QPushButton:hover  {{ background:#B4D0FF; }}
            QPushButton:disabled {{ background:#444; color:#888; }}
            QGroupBox {{
                border:1px solid {COLOR_ACCENT}; border-radius:6px;
                margin-top:8px; font-weight:bold; color:{COLOR_ACCENT};
            }}
            QGroupBox::title {{ subcontrol-origin:margin; left:8px; }}
            QTableWidget {{
                background:{COLOR_PANEL}; color:{COLOR_TEXT};
                gridline-color:#444; border:none;
            }}
            QHeaderView::section {{
                background:{COLOR_HEADER}; color:white;
                font-weight:bold; border:none; padding:4px;
            }}
            QScrollArea {{ border:none; }}
            QLabel {{ color:{COLOR_TEXT}; }}
            QLineEdit, QSpinBox, QComboBox {{
                background:{COLOR_PANEL}; color:{COLOR_TEXT};
                border:1px solid {COLOR_ACCENT}; border-radius:4px; padding:3px;
            }}
            QTextEdit {{
                background:{COLOR_PANEL}; color:{COLOR_TEXT};
                border:1px solid #444; border-radius:6px;
            }}
        """)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter)

        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([420, 780])

    # ── LEFT panel: input ─────────────────────────────────────────────────────

    def _build_left_panel(self):
        panel = QWidget()
        lay   = QVBoxLayout(panel)
        lay.setSpacing(8)

        # ── number of states / inputs ────────────────────────────────────────
        cfg_box = QGroupBox("Configuration")
        cfg_lay = QGridLayout(cfg_box)

        cfg_lay.addWidget(QLabel("Number of states:"), 0, 0)
        self.spin_states = QSpinBox()
        self.spin_states.setRange(2, 12)
        self.spin_states.setValue(4)
        cfg_lay.addWidget(self.spin_states, 0, 1)

        cfg_lay.addWidget(QLabel("Number of inputs:"), 1, 0)
        self.spin_inputs = QSpinBox()
        self.spin_inputs.setRange(1, 6)
        self.spin_inputs.setValue(2)
        cfg_lay.addWidget(self.spin_inputs, 1, 1)

        btn_build = QPushButton("Build Table")
        btn_build.clicked.connect(self._build_input_table)
        cfg_lay.addWidget(btn_build, 2, 0, 1, 2)

        lay.addWidget(cfg_box)

        # ── state / input name editors ───────────────────────────────────────
        names_box = QGroupBox("State & Input Names")
        names_lay = QVBoxLayout(names_box)

        self.state_names_edit = QLineEdit("A,B,C,D")
        self.state_names_edit.setPlaceholderText("Comma-separated state names")
        names_lay.addWidget(QLabel("States (comma-separated):"))
        names_lay.addWidget(self.state_names_edit)

        self.input_names_edit = QLineEdit("X=0,X=1")
        self.input_names_edit.setPlaceholderText("Comma-separated input labels")
        names_lay.addWidget(QLabel("Inputs (comma-separated):"))
        names_lay.addWidget(self.input_names_edit)

        lay.addWidget(names_box)

        # ── data entry table ─────────────────────────────────────────────────
        tbl_box = QGroupBox("State Table  (format: NextState,Output  or  -,-)")
        tbl_lay = QVBoxLayout(tbl_box)

        hint = QLabel(
            "Each cell: NextState,Output\n"
            "Use '-' for don't-care. E.g.: A,0  or  -,-  or  B,01"
        )
        hint.setStyleSheet("font-size:11px;color:#888;")
        tbl_lay.addWidget(hint)

        self.input_table = QTableWidget(0, 0)
        self.input_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl_lay.addWidget(self.input_table)
        lay.addWidget(tbl_box, 1)

        # ── example buttons ───────────────────────────────────────────────────
        ex_box = QGroupBox("Load Example")
        ex_lay = QHBoxLayout(ex_box)
        for lbl, fn in [
            ("Q1 (lecture)", self._load_example_q1),
            ("Q2 (incomplete)", self._load_example_q2),
            ("Q3 (incomplete)", self._load_example_q3),
        ]:
            b = QPushButton(lbl)
            b.clicked.connect(fn)
            ex_lay.addWidget(b)
        lay.addWidget(ex_box)

        # ── run button ────────────────────────────────────────────────────────
        self.btn_run = QPushButton("▶  Run Minimization")
        self.btn_run.setFixedHeight(40)
        self.btn_run.clicked.connect(self._run)
        lay.addWidget(self.btn_run)

        return panel

    # ── RIGHT panel: visualisation ────────────────────────────────────────────

    def _build_right_panel(self):
        panel = QWidget()
        lay   = QVBoxLayout(panel)
        lay.setSpacing(8)

        # Step log
        log_box = QGroupBox("Step-by-Step Log")
        log_lay = QVBoxLayout(log_box)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 10))
        self.log_text.setMinimumHeight(90)
        self.log_text.setMaximumHeight(120)
        log_lay.addWidget(self.log_text)
        lay.addWidget(log_box)

        # Step navigation
        nav_box = QGroupBox("Navigation")
        nav_lay = QHBoxLayout(nav_box)
        self.btn_prev = QPushButton("◀  Previous")
        self.btn_prev.setEnabled(False)
        self.btn_prev.clicked.connect(self._prev_step)
        self.btn_next = QPushButton("Next  ▶")
        self.btn_next.setEnabled(False)
        self.btn_next.clicked.connect(self._next_step)
        self.btn_auto = QPushButton("⏵  Auto Play")
        self.btn_auto.setEnabled(False)
        self.btn_auto.clicked.connect(self._auto_play)
        self.step_label = QLabel("Step: 0 / 0")
        self.step_label.setAlignment(Qt.AlignCenter)
        nav_lay.addWidget(self.btn_prev)
        nav_lay.addWidget(self.step_label)
        nav_lay.addWidget(self.btn_next)
        nav_lay.addWidget(self.btn_auto)
        lay.addWidget(nav_box)

        # Implication table (scrollable)
        impl_box = QGroupBox("Implication Table")
        impl_lay = QVBoxLayout(impl_box)
        self.impl_scroll = QScrollArea()
        self.impl_scroll.setWidgetResizable(False)
        self.impl_scroll.setMinimumHeight(420)
        impl_lay.addWidget(self.impl_scroll)
        lay.addWidget(impl_box, 3)

        # Results
        res_box  = QGroupBox("Results")
        res_lay  = QHBoxLayout(res_box)

        # Equivalence classes
        eq_grp = QGroupBox("Equivalence Classes")
        eq_lay = QVBoxLayout(eq_grp)
        self.equiv_label = QLabel("—")
        self.equiv_label.setWordWrap(True)
        self.equiv_label.setFont(QFont("Courier New", 11))
        eq_lay.addWidget(self.equiv_label)
        res_lay.addWidget(eq_grp, 1)

        # Reduced table
        red_grp = QGroupBox("Reduced State Table")
        red_lay = QVBoxLayout(red_grp)
        self.reduced_table_widget = QTableWidget(0, 0)
        self.reduced_table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        red_lay.addWidget(self.reduced_table_widget)
        res_lay.addWidget(red_grp, 2)

        lay.addWidget(res_box)

        # Timer for auto-play
        self.timer = QTimer()
        self.timer.setInterval(1200)   # ms between steps
        self.timer.timeout.connect(self._next_step)

        return panel

    # ── input table builder ───────────────────────────────────────────────────

    def _build_input_table(self):
        states = [s.strip() for s in self.state_names_edit.text().split(',') if s.strip()]
        inputs = [i.strip() for i in self.input_names_edit.text().split(',') if i.strip()]

        n_s = self.spin_states.value()
        n_i = self.spin_inputs.value()

        # Pad or truncate name lists
        while len(states) < n_s:
            states.append(chr(65 + len(states)))
        states = states[:n_s]
        while len(inputs) < n_i:
            inputs.append(f"X{len(inputs)}")
        inputs = inputs[:n_i]

        self.state_names_edit.setText(','.join(states))
        self.input_names_edit.setText(','.join(inputs))

        self.input_table.setRowCount(n_s)
        self.input_table.setColumnCount(n_i)
        self.input_table.setVerticalHeaderLabels(states)
        self.input_table.setHorizontalHeaderLabels(inputs)

        # Fill empty cells with placeholder
        for r in range(n_s):
            for c in range(n_i):
                if not self.input_table.item(r, c):
                    self.input_table.setItem(r, c, QTableWidgetItem('-,-'))

    # ── example loaders ───────────────────────────────────────────────────────

    def _load_example(self, states, inputs, rows):
        """Generic loader."""
        self.spin_states.setValue(len(states))
        self.spin_inputs.setValue(len(inputs))
        self.state_names_edit.setText(','.join(states))
        self.input_names_edit.setText(','.join(inputs))
        self._build_input_table()
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.input_table.setItem(r, c, QTableWidgetItem(val))

    def _load_example_q1(self):
        """
        Q1 from lecture slide 7 — completely specified machine.
        States: A B C D  |  Inputs: X=0, X=1
        """
        states = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        inputs = ['X=0', 'X=1']
        rows = [
            ['E,1', 'E,1'],   # A
            ['C,1', 'E,1'],   # B
            ['I,0', 'H,0'],   # C
            ['H,1', 'A,1'],   # D
            ['I,0', 'F,0'],   # E
            ['E,0', 'G,0'],   # F
            ['H,1', 'B,1'],   # G
            ['C,0', 'D,0'],   # H
            ['F,1', 'B,1'],   # I
        ]
        self._load_example(states, inputs, rows)

    def _load_example_q2(self):
        """
        Q2 from lecture slide 8 — incompletely specified (don't-cares).
        States: A B C D E F  |  Inputs: XY=00, XY=01, XY=10, XY=11
        """
        states = ['A', 'B', 'C', 'D', 'E', 'F']
        inputs = ['XY=00', 'XY=01', 'XY=10', 'XY=11']
        rows = [
            ['A,0',  'C,0',  'E,0',  'D,0'],   # A
            ['D,0',  'E,0',  'E,0',  'A,0'],   # B
            ['E,1',  'A,1',  'F,1',  'B,1'],   # C
            ['B,0',  'C,0',  'C,0',  'B,0'],   # D
            ['C,1',  'D,1',  'F,1',  'A,1'],   # E
            ['F,1',  'B,1',  'A,1',  'D,1'],   # F
        ]
        self._load_example(states, inputs, rows)

    def _load_example_q3(self):
        """
        States: A B C D E F G  |  Inputs: XY=00, XY=01, XY=10, XY=11
        """
        states = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        inputs = ['XY=00', 'XY=01', 'XY=10', 'XY=11']
        rows = [
            ['A,0',  'E,1',  '-,-',  'D,0'],   # A
            ['-,-',  'C,0',  'B,0',  'D,1'],   # B
            ['A,0',  'C,0',  '-,-',  '-,-'],   # C
            ['A,0',  '-,-',  '-,-',  'D,1'],   # D
            ['-,-',  'E,1',  'F,1',  '-,-'],   # E
            ['-,-',  'E,0',  'F,1',  'G,1'],   # F
            ['A,0',  '-,-',  '-,-',  'G,1'],   # G
        ]
        self._load_example(states, inputs, rows)

    # ── run ───────────────────────────────────────────────────────────────────

    def _run(self):
        # Parse state/input names
        states = [s.strip() for s in self.state_names_edit.text().split(',') if s.strip()]
        inputs = [i.strip() for i in self.input_names_edit.text().split(',') if i.strip()]

        if len(states) < 2:
            QMessageBox.warning(self, "Error", "Need at least 2 states.")
            return

        n_r = self.input_table.rowCount()
        n_c = self.input_table.columnCount()
        if n_r != len(states) or n_c != len(inputs):
            QMessageBox.warning(
                self, "Error",
                "Table dimensions don't match state/input counts.\n"
                "Click 'Build Table' first."
            )
            return

        # Parse the table
        table = {}
        try:
            for r, s in enumerate(states):
                row = []
                for c in range(n_c):
                    item = self.input_table.item(r, c)
                    raw  = item.text() if item else '-,-'
                    ns, out = parse_cell(raw)
                    # Validate next-state references
                    if ns and ns not in states:
                        raise ValueError(
                            f"Unknown next state '{ns}' in row {s}, input {inputs[c]}"
                        )
                    row.append((ns, out))
                table[s] = row
        except ValueError as e:
            QMessageBox.critical(self, "Parse Error", str(e))
            return

        # Run the algorithm
        self.solver    = ImplicationTableSolver(states, inputs, table)
        self.step_idx  = 0
        self.all_steps = self.solver.steps

        # Build implication table widget
        impl_widget = ImplicationTableWidget(states, self.solver.pairs)
        self.impl_widget = impl_widget
        self.impl_scroll.setWidget(impl_widget)

        # Enable navigation
        self.btn_prev.setEnabled(False)
        self.btn_next.setEnabled(True)
        self.btn_auto.setEnabled(True)

        # Show step 0
        self._show_step(0)

    # ── navigation ────────────────────────────────────────────────────────────

    def _show_step(self, idx):
        self.step_idx = idx
        n = len(self.all_steps)
        self.step_label.setText(f"Step: {idx + 1} / {n}")
        self.btn_prev.setEnabled(idx > 0)
        self.btn_next.setEnabled(idx < n - 1)

        desc, status = self.all_steps[idx]

        # Update log
        self.log_text.setPlainText(f"[Step {idx + 1}]\n{desc}")

        # Update implication table colours
        self.impl_widget.update_cells(status, self.solver)

        # On the last step, show results
        if idx == n - 1:
            self._show_results()

    def _prev_step(self):
        if self.step_idx > 0:
            self._show_step(self.step_idx - 1)

    def _next_step(self):
        if self.step_idx < len(self.all_steps) - 1:
            self._show_step(self.step_idx + 1)
        else:
            self.timer.stop()
            self.btn_auto.setText("⏵  Auto Play")

    def _auto_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn_auto.setText("⏵  Auto Play")
        else:
            self.timer.start()
            self.btn_auto.setText("⏸  Pause")

    # ── results ───────────────────────────────────────────────────────────────

    def _show_results(self):
        # Equivalence classes
        classes = self.solver.equiv_classes
        label_names = 'XYZWVUTSRQPONMLKJIHGFEDCBA'
        lines = []
        for i, cls in enumerate(classes):
            lbl = label_names[i] if i < len(label_names) else f"S{i}"
            lines.append(f"  {lbl} = {{{', '.join(cls)}}}")
        self.equiv_label.setText('\n'.join(lines))

        # Reduced state table
        inputs  = self.solver.inputs
        r_states = self.solver.reduced_states
        r_table  = self.solver.reduced_table

        n_cols = 1 + len(inputs)   # state column + one per input
        self.reduced_table_widget.setRowCount(len(r_states))
        self.reduced_table_widget.setColumnCount(n_cols)
        headers = ['State'] + inputs
        self.reduced_table_widget.setHorizontalHeaderLabels(headers)

        for row, st in enumerate(r_states):
            # State name cell
            item = QTableWidgetItem(st)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QColor(COLOR_HEADER))
            item.setForeground(QColor('white'))
            self.reduced_table_widget.setItem(row, 0, item)

            # Data cells
            for col, (ns, out) in enumerate(r_table[st]):
                text = f"{ns},{out}"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.reduced_table_widget.setItem(row, col + 1, item)


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("State Minimizer")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
