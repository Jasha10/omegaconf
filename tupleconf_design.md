Current support for tuples os as follows:
```python
>>> OmegaConf.create({"t": (123,)})
{'t': [123]}
```
Some support for tuple type annotations in structured configs is given, but only the first type hint in the tuple is considered.
E.g. Tuple[int, str] and Tuple[int, int] and Tuple[int, ...] are all treated by OmegaConf as equivalent to List[int].

In implementing tuple support in OmegaConf, consider the following examples:

to_yaml = OmegaConf.to_yaml
create = OmegaConf.create

isinstance(create(to_yaml(create({"i": 123})))["i"], int)
isinstance(create(to_yaml(create({"s": "123"})))["s"], str)
isinstance(create(to_yaml(create({"l": [123]})))["l"], ListConfig)
isinstance(create(to_yaml(create({"d": {"i": 123}})))["d"], DictConfig)
isinstance(create(to_yaml(create({"t": (123)})))["t"], ???)  # Should be TupleConf or ListConf

The issue though is that yaml does not have a native distinction between tuple and list types.
pyyaml, which OmegaConf uses as a backed, does support python tuple tags, however:
```python
>>> import yaml  # pyyaml
>>> s = yaml.dump({"t": (123,)})
>>> print(s)
t: !!python/tuple
- 123

>>> yaml.unsafe_load(s)
{'t': (123,)}
>>> yaml.safe_load(s)
Traceback (most recent call last):
  ...
yaml.constructor.ConstructorError: could not determine a constructor for the tag 'tag:yaml.org,2002:python/tuple'
  in "<unicode string>", line 1, column 4:
    t: !!python/tuple
       ^

```
Figure lwkejf

Options for tuple support:
- keep the status quo. Ask people to instantiate `_target_: builtins.tuple`, or lean on hydra-zen's tuple support.
  - Drawback: the support for tuple type-annotations is half-baked. This feature is fairly popular.
- Implement a new subclass of BaseContainer: TupleConf.
- Implement a flag that changes ListConfig into "tuple mode".

Options for serialization:
- serialize to yaml as a sequence; upon deserializing, convert to tuple if the type annotation says so.
  - Drawback: this kills data round-tripping. Specifically, in the absece of a structured config, calling `create(to_yaml({"t": (123,)}))`
    would result in `{"t": [123]}` rather than in  `{"t": (123,)}`.
  - Advantage: compatible with yaml.safe_load out-of-the-box
- serialize using the `!!python/tuple` tag.
  - Advantage: more faithful round-tripping of data between OmegaConf and yaml. I feel this point is important.
  - Drawbacks:
    - Makes the yaml file less pretty if there are `!!python/tuple` tags.
    - Incompatible with yaml.safe_load (see the aboce example in Figure lwkejf).
