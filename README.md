# A Collection of Solvers

A collection of solvers for various minigames and puzzles.

Each solver lives on its own branch so the full development history of every project is preserved.

## Solvers

| Branch | Game / Puzzle | Language | Status | Description |
| --- | --- | --- | --- | --- |
| `wordle-solver` | wordle | Python | Finished | Solves wordle using information theory |
| `poople-solver` | poople | Python | Finished | Solves poople efficiently with BFS |
| `15-puzzle-solver` | 15 puzzle | Python | Unfinished | Solves 15 puzzle |

## How to search and use a solver

For a quick search, press Ctrl+F to search for a puzzle you are looking for.

To use a specific solver, either:

```
# Clone a single branch (Recommended)
git clone -b <branch_name> --single-branch https://github.com/johntyc10/a-collection-of-solvers.git <branch_name>
cd <branch_name>
```

OR

```
# Clone the whole repository
git clone https://github.com/johntyc10/a-collection-of-solvers.git
cd a-collection-of-solvers

# Switch to a specific solver
git checkout <branch_name>
```

And then follow the per-solver instructions in the README.md. All per-solver instructions assumes you followed the above instructions and is in the solver branch.

Each branch is a self-contained project with its own code, README, and history.

## Philosophy

**Note:** These projects are mostly written by hand. AI tools may have been used occasionally for small suggestions, debugging, or writing READMEs, but the core logic, structure, and algorithms are human-written and human-approved.

## Contributions

Contributions are welcome! Feel free to open issues, suggest new solvers, improve existing ones, or submit pull requests.

## License

This repository is released under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0). See `LICENSE` for details.
