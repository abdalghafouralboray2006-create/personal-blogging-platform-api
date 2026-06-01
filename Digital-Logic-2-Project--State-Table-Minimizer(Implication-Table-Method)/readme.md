# State Table Minimizer
A Python + PyQt5 desktop application for minimizing finite-state machines using the Implication Table Method taught in Digital Logic Design courses.
The application visualizes every stage of the minimization process and allows users to follow the algorithm step-by-step exactly as performed manually in lectures.
## Features
 * Complete implementation of the Implication Table Method
 * Supports completely specified state machines
 * Supports incompletely specified state machines with don't-cares ("-")
 * Interactive GUI built with PyQt5
 * Step-by-step visualization of the algorithm
 * Automatic dependency propagation
 * Equivalence class generation
 * Reduced state table generation
 * Built-in lecture examples
 * Auto-play walkthrough mode

## Installation
### Clone the Repository
```
git clone https://github.com/Wael-06/experimental-lab/new/main/Digital-Logic-2-Project--State-Table-Minimizer(Implication-Table-Method)

```
### Install Dependencies
```
pip install PyQt5

```
### Run
```
python state_minimizer.py

```
## Input Format
Each cell follows the format: NextState,Output
| Meaning | Input |
|---|---|
| Next state A, output 0 | "A,0" |
| Next state B, output 01 | "B,01" |
| Don't-care next state and output | "-,-" |
| Defined state, don't-care output | "A,-" |
| Don't-care state, output 1 | "-,1" |
## How to Use
 1. **Configure the Machine**: Choose the number of states and inputs. Optionally rename states and inputs.
 2. **Build the Table**: Press **Build Table** to generate the editable state table.
 3. **Enter State Data**: Fill each cell using the NextState,Output format.
 4. **Run Minimization**: Press **Run Minimization**. The solver will execute the complete implication table algorithm.
 5. **Navigate Through Steps**: Use **Previous**, **Next**, or **Auto Play** to see the implication table update after every algorithm stage.
## Algorithm Overview
 * **Step 1 - Output Compatibility Check**: Pairs whose outputs differ for at least one input are immediately marked incompatible.
 * **Step 2 - Dependency Collection**: Compatible pairs generate dependency conditions based on their next states.
 * **Step 3 - Dependency Propagation**: If a dependency becomes incompatible, every pair depending on it also becomes incompatible.
 * **Step 4 - Compatible Pair Detection**: All remaining unmarked pairs are marked compatible.
 * **Step 5 - Equivalence Class Construction**: Union-Find (Disjoint Set Union) merges compatible states into equivalence classes.
 * **Step 6 - Reduced State Table Generation**: Each equivalence class becomes a new reduced state and a minimized state table is generated.
## Built-in Examples
 * **Q1 (Lecture Example)**: 9 states, completely specified machine.
 * **Q2 (Incomplete Machine)**: 6 states, uses don't-care entries.
 * **Q3 (Incomplete Machine)**: 7 states, demonstrates dependency propagation.
## Project Structure
```
state_minimizer.py
│
├── Helper Functions
│   ├── parse_cell()
│   ├── outputs_compatible()
│   └── next_states_pair()
│
├── ImplicationTableSolver
│   ├── Pair generation
│   ├── Dependency tracking
│   ├── Propagation engine
│   ├── Equivalence classes
│   └── Reduced table generation
│
├── ImplicationTableWidget
│   └── Implication table visualization
│
└── MainWindow
    ├── User input
    ├── Step navigation
    ├── Visualization
    └── Results display

```
## Technologies Used
 * **Python 3**
 * **PyQt5**
 * Standard library modules: sys, copy
## Educational Purpose
This project was developed as part of the Digital Logic 2 course and demonstrates the complete Implication Table Method for finite-state machine minimization.
## Author
**Youssef Wael**
Computer and Communication Engineering
Faculty of Engineering, Alexandria University

