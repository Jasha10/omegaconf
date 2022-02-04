# Merge strategy enabling `ListConfig` concatenation



**Is your feature request related to a problem? Please describe.**

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.


## Abstract
This document proposes 

## Introduction
`OmegaConf.merge` is one of the most important methods exported by this library. [Hydra](hydra.cc), which is OmegaConf's highest-profile client, uses `OmegaConf.merge` as the workhorse to accomplish "config composition".

OmegaConf.merge
## API
Two 
- Using a keyword-only argument to `OmegaConf.merge`:
```python
OmegaConf.merge(cfg1, cfg2, ...)  # default strategy
OmegaConf.merge(cfg1, cfg2, ..., strategy="overwrite_lists")  # equivalent
OmegaConf.merge(cfg1, cfg2, ..., strategy="concatenate_lists")  # the new strategy
```
- Using a different entrypoint under the `omegaconf.OmegaConf` interface:
```python
OmegaConf.merge(cfg1, cfg2, ...)  # default strategy
OmegaConf.merge_concat(cfg1, cfg2, ...)  # the new strategy
```

## Specification
```python
# a more complex example
merge1([1,2,3], [4,5])  == [4,5]
merge2([1,2,3], [4,5])  == [1,2,3,4,5]

# a more complex example
merge1({"foo": [1,2,3]}, {"foo": [4,5]})  == {"foo": [4,5]}
merge2({"foo": [1,2,3]}, {"foo": [4,5]})  == {"foo": [1,2,3,4,5]}
```
## Use Cases
A big part of the vision for Hydra is the ability to call or instantiate python
objects based on settings that are selected dynamically, e.g. via the command line.
Realizing this vision relies on being able to configuration whose structure mirrors the
API of the python object that is to be called.

(This is starting to feel like it should belong in a Hydra design doc rather than an OmegaConf doc).

## Implementation
## References

### Hydra issues
[Implement #1389 or similar functionality #1939](https://github.com/facebookresearch/hydra/issues/1939)
[Bug Parsing list of configurations with a structured config #1389](https://github.com/facebookresearch/hydra/issues/1389)
[Feature Request Append to a list from command line #1547](https://github.com/facebookresearch/hydra/issues/1547)
[list of a default config #1926](https://github.com/facebookresearch/hydra/issues/1926)
