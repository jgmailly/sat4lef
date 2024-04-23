# sat4lef
We use SAT-based techniques for Local Envy-Freeness (LEF) issues in fair division of indivisible goods. This script can find a LEF allocation if there exists one, or provide explanations (based on MUSes of the SAT encoding) for the non-existence of LEF allocations otherwise.
It requires [pysat](https://pypi.org/project/python-sat/], [NetworkX](https://pypi.org/project/networkx/) and [GraphViz](https://pypi.org/project/graphviz/).

## Command-line

```bash
usage: main.py [-h] [-o OUT] [--mus] [--enummin] [--minagent] [--verbose] [--redundant] pref_file social_file

positional arguments:
  pref_file          path to the preference file
  social_file        path to the social file

options:
  -h, --help         show this help message and exit
  -o OUT, --out OUT  optional file to print the output (append)
  --mus              if set compute a mus instead of the allocation (only works if formula is unsat)
  --enummin          enumerate the min MUSes (must be used in addition to --mus)
  --minagent         focuses on minimal MUSes that minimize the number of agents (must be used in addition to --mus)
  --verbose          print more information
  --redundant        add redundant structural clauses

```

## Input files
The preferences of the agents are given in a text file following this
format:
```
agent1:object1 object2 ... objectN
...
agentN:object1 object2 ... objectN
```
Each line describes the preferences of an agent. The line starts with
the agent name, a colon, and then the list of objects in decreasing
order of preference (seperated with white spaces).

The social network is represented as a TGF file:
```
agent1
...
agent2
#
agent1 agent2
agent2 agent3
...
```
Before the `#` symbol, each line contains the name of an agent. After
this symbol, each line contains the names of two agents which are
connected in the network.

The preferences file and social network file must only differ by their extension, i.e.
- preferences are stored in `path/to/file.pref`,
- the social network is stored in `path/to/file.soc`.

## Output
If the option `--mus` is not set, the default behavior of the program
is to solve the decide-LEF problem, i.e. it determines whether there
is a LEF allocation, and it
- prints the allocation if it exists,
- prints `NO`if there is no such allocation.

If the `--mus` option is set, then the program extracts a MUS from the
unsatisfiable SAT encoding of the instance, or prints `NO`if the
instance is satisfiable (in which case there is no MUS).
