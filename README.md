# sat4lef
We use SAT-based techniques for Local Envy-Freeness issues in fair division of indivisible goods

## Command-line

```bash
usage: main.py [-h] [-o OUT] [--mus] pref_file social_file

positional arguments:
  pref_file          path to the preference file
  social_file        path to the social file

options:
  -h, --help         show this help message and exit
  -o OUT, --out OUT  optional file to print the output (append)
  --mus              if set compute a MUS instead of the allocation (only works if the instance is not LEF)
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

## Output
If the option `--mus`is not set, the default behavior of the program
is to solve the decide-LEF problem, i.e. it determines whether there
is a LEF allocation, and it
- prints the allocation if it exists,
- prints `NO`if there is no such allocation.

If the `--mus` option is set, then the program extracts a MUS from the
unsatisfiable SAT encoding of the instance, or prints `NO`if the
instance is satisfiable (in which case there is no MUS).
