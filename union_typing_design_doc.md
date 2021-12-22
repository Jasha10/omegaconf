# Union typing design: Initial thoughts
Considerations:
- MISSING value assigned to Union
- The node should stll be a union node after assignment and after merging (where the union is on the left, but not if the union is on the right??)


## None value assigned to Union
It should be legal to assign a `None` value to a union field with any of the following type hints:
- `Optional[Union[...]]`
- `Union[Optional[...], ...]`
- `Union[None, ...]`

## Type Coersion in Assignment or Merge of Union-Typed Fields

See my comment on OmegaConf issue [ StructuredConfig from recursive dataclass #843 ](https://github.com/omry/omegaconf/issues/843)

Currently assignment of an `int` to to a float-typed field will result in
conversion of the int to a float (e.g. in assignment to a field with type hint
`int`, or in adding to a dictionary with annotation `Dict[str, int]`).

What happens when an `int` is assigned to a field of type Union[float, int]?
What if it is assigned to a field of type Union[int, float]?

What about the case of strings such as "123"? Currently, assigning such a field

How about assigning one of the dictionaries `{"name": "bond", "age": 7}` or `{"age": 7}` to a field with any of the following type hints?
- `Union[User, Any]`
- `Union[Any, UserWithDefaultName]`
- `Union[UserWithDefaultName, Dict[str, Any]]`
- `Union[Dict[Any, int], UserWithDefaultName]`
- `Union[UserWithDefaultName, Dict[str, Union[str, int]]]`
- `Union[Dict[Union[str, int], int], UserWithDefaultName]`
- `Union[UserWithDefaultName, Dict[str, Union[int, str]]]`
- `Union[Dict[Union[int, str], int], UserWithDefaultName]`
In the above cases, I feel that the assgnment should be treated as `UserWithDefaultName`, 

Re-using validation logic from other nodes


Are there some situations in which we would want to raise an error saying that the assignment is ambiguous?

Possible strategies regarding conversion upon assignment/merge to a union-typed field:
- Do convert, with special casing for e.g. assigning the number `123` to a field with type hint `Union[int, float]` or `Union[float, int]`.
  Drawbacks: The number of special cases might be large, and the logic might get complicated.
  It is previously been discussed that conversion of `"123"` to an `int` upon assignment to an `IntegerNode` may not be the best 
- Do not convert, except for converting to structured config.
  This means that assignment of the string "123" to a union-typed field Union[int, str] will unambiguously treat "123" as a string.
  Some logic for handling the case of `Union[User, Dict[str, Any]]` or `Union[User, Dict[str, Union[str, int]]]` will still be necessary.
A relatively easy way to handle ambiguity regarding which type to convert to would be to say that the assignment of `val` to
field `cfg.u` will be pigeonholed into the leftmost union arg that is compatible with `val`.
This means that `Union[User, Dict[str, Any]]` behaves differently from `Union[Dict[str, Any], User]`:
- `Union[User, Dict[str, Any]]` treats assigned values as 
- `Union[Dict[str, Any], User]`






Ideally, a `UnionNode` should be able to wrap either a leaf node (such as
`IntegerNode`) or a non-leaf node (such as a `DictConfig`). How does a
UnionNode interact with methods such as `OmegaConf.is_list`(...)?

## Interaction with `OmegaConf` methods.

Suppose `cfg.u` is typed as a union. The methods of the `OmegaConf` class should behave as follows:

### `OmegaConf.is_optional(cfg.u)`
Should be True only if `cfg.u` has one of the following type hints:
- `Optional[Union[...]]`
- `Union[Optional[...], ...]`
- `Union[None, ...]`  (or `Union[NoneType, ...]`)

## Interaction with classmethods
Suppose `cfg.u` is union-typed.
What happens when you call one of the `cfg.u.__getitem__` or `cfg.u.__getattr__` methods?
That should depend on the value of `cfg.u`. For example, if `cfg.u` has type-hint `Union[str, Dict[str, int]]`,

Should users interact with `UnionNodes`?

## Interaction with interpolations
If `cfg.u` is an interpolation with a Union type hint, union type validation should
occur at the time when the node is dereferenced.
This is consistent with how non-union interpolations are validated, right?

## Other considerations
Currently in python it is legal to duplicate arguments in unions, e.g.
`Union[int, float, int]`. OmegaConf should be able to handle such duplicated arguments.


# Should users be allowed to interact with `UnionNode` instances?
Currently:
- Leaf nodes types (such as `IntegerNode`) are hidden from users, and the
  values wrapped by those leaf nodes are exposed transparently.
  For example, if `cfg.i` has type hint `int`, users will see `type(cfg.i) == int`, not `type(cfg.i) == IntegerNode`.
- Container nodes types are exposed to users, with the API of e.g. `DictConfig` being designed to mimic that of `dict`.
  For example, if `cfg.d` has type hint `Dict[str, str]`, users will see `type(cfg.i) == DictConfig`, not `type(cfg.i) == dict`.

Now, suppose that `cfg.u` has type `Union[int, Dict[str, int]]`.
- If `cfg.u` is assigned the value `123`, we should have `type(cfg.u) == int` (to maintain API consistency with e.g. `type(cfg.i) == int`).
- If `cfg.u` is assigned the value `{"foo": 456}`, we should have either `type(cfg.u) == UnionNode` or `type(cfg.u) == DictConfig`.
- The former option, exposing `UnionNode` to users such that `type(cfg.u) == UnionNode` if a dictionary valie has been assigned to `cfg.u`,
  would require defining `cfg.__getattr__` and `cfg.__getitem__` methods passing through calls to the wrapped `DictConfig` instance.
  The latter option might be easier to implement, defining `UnionNode` as a subclass of `ValueNode`.

  In particular, defining `UnionNode` as a subclass of `ValueNode` would allow
  existing logic to handle `UnionNode` by calling e.g. union_node._value (see
  e.g. `_utils.py:_get_value`, which branches based on whether the given input
  `value` is a `ValueNode` or a `Container`).

  Then again, what if the union node wraps e.g. an `IntegerNode`? We would want `_get_value` to return an `int`, not an instance of `IntegerNode`.
  If `UnionNode` is a subclass of `ValueNode` and if a given `union_node` wraps an `IntegerNode`, then calling `union_node._value` would
  return an `IntegerNode`, not an instance of `int`, right? (Unless if we
  special-case the `UnionNode._value` function, which may be a viable option).

In either case, the type of value returned by `getattr(cfg, "u")` will depend on the value that is wrapped by the union node.
If the value `{"foo": "bar"}` is assigned to a field `cfg.u` that has type hint `Union[int, Dict[str, str]]`,
what should we have `type(cfg.u) == DictConfig` or `type(cfg.u) == UnionNode`?


## Implementation Details: Where does `UnionNode` fit into the OmegaConf class heirarchy?
Currently, OmegaConf's class heirarchy looks like this:
- Node
  - Container
    - BaseContainer
      - DictConfig
      - ListConfig
  - ValueNode
    - AnyNode
    - StringNode
    - IntegerNode
    - FloatNode
    - BooleanNode
    - EnumNode
    - InterpolationResultNode
In a given config tree, `ValueNode` instances represent leafs of the tree (with the exception of `InterpolationResultNode` instances),
while `Container` instances represent non-leaf nodes in the tree.

Is `UnionNode` similar to `InterpolationResultNode` in that both are
transient passthrough nodes? Does it make sense to have `UnionNode` be a
subclass of `ValueNode`?

I think that `UnionNode` fits the `ValueNode` API in that a union node will wrap a single value.
The value wrapped by a `UnionNode` would be another node.
This differs from existing `ValueNode` implementations, which typically wrap a raw leaf node (with the exception of `InterpolationResultNode`).

If we implement `UnionNode` as a subclass of `ValueNode`, we may wish to
override the `ValueNode._value` method so that additional unwrapping is
performed (to avoid e.g. an `IntegerNode` being returned by a call to `union_node._value`; an `int` should be returned instead, right?)
An alternative to performing additional unwrapping in `ValueNode._value` would be to nor store wrapped leaf node values in the first place.
For example, instead of storing an `IntegerNode` isntance, we could store an
`int` instance. This is what pereman2 did in his union typing PR.




From the user's perspective, a field typed as 

Handling nested unions:
Suppose that a user writes a type hint like this:
```python
  Union[int, User, Union[...]]
```
We could either flatten the union or not flatten it.
Flattening would be easier? And optionality could be flattened out too. Deduplication of args could happen at the same time.

Python version 3.10 supports the `__or__` syntax for defining unions, i.e. `Union[int, str]` is equivalent to `int | str` (see [PEP 604](https://www.python.org/dev/peps/pep-0604/)).


Many thanks to @pereman2 for his pioneering work on an initial PR to implement union typing.





From my comment on OmegaConf issue [ StructuredConfig from recursive dataclass #843 ](https://github.com/omry/omegaconf/issues/843):
One thing that has been on my mind is the question of how to handle ambiguity, where a value assigned to a union-typed structured config field could be interpreted as one of several types that are present in the union type hint. For example:
```python
from omegaconf import OmegaConf, MISSING

@dataclass
class Schema():
    task_or_dict: TaskConfig | Dict[str, Any] = MISSING

cfg = OmegaConf.create(Schema)
cfg.task_or_dict = {"tasks": "foo"}
```
The question is, in the last line above, should the assigned value be treated as a `TaskConfig` or as a `Dict[str, Any]`?

So far I can think of two ways to resolve such ambiguity:
1. type the value as belonging to the leftmost compatible argument appearing in the union. In the example above, the assignment of `{"tasks": "foo"}` would be typed as `TaskConfig` (not `Dict[str, Any]`) because `TaskConfig` appears further to the left in the type hint `TaskConfig | Dict[str, Any]`. This would let users decide how to handle ambiguity by ordering the arguments to their union type hint.
2. Create special rules that "do the right thing", e.g. giving precedence to structured configs when possible. In the example above, `{"tasks": "foo"}` would be typed as `TaskConfig` because `TaskConfig` is a structured config.

I am leaning towards option 1 above because I think it would be relatively easier to implement, and not overly complicated for users to reason about.
