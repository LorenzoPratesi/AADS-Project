from six import add_metaclass

from sage.structure.list_clone import ClonableArray
from sage.combinat.abstract_tree import (AbstractClonableTree,
                                         AbstractLabelledClonableTree)
from sage.combinat.ordered_tree import LabelledOrderedTrees
from sage.rings.integer import Integer
from sage.misc.inherit_comparison import InheritComparisonClasscallMetaclass
from sage.misc.classcall_metaclass import ClasscallMetaclass
from sage.misc.lazy_attribute import lazy_attribute
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.arith.all import binomial
from sage.sets.non_negative_integers import NonNegativeIntegers
from sage.sets.disjoint_union_enumerated_sets import DisjointUnionEnumeratedSets
from sage.sets.family import Family
from sage.misc.cachefunc import cached_method
from lib.backtraking import *


@add_metaclass(InheritComparisonClasscallMetaclass)
class MAryTree(AbstractClonableTree, ClonableArray):
    r"""
    The class of `m`-ary trees.

    An `m`-ary tree (where `m` is a positive integer) is a
    structure that is either a *leaf* or a *node*.
    A leaf carries no information.
    A node is given by a list of `m` arbitrary `m`-ary trees
    (called its *children*).

    INPUT:

    - `m` -- the arity

    - ``children`` -- ``None`` (default) or a list, tuple or iterable of
      length `m` of `m`-ary trees or convertible objects.

    - ``check`` -- (default to ``True``) whether check for `m`-arity should be
      performed or not.

    EXAMPLES::

        sage: MAryTree(3)
        .
        sage: MAryTree(3, [])
        [., ., .]
        sage: MAryTree(3, [None, [], None])
        [., [., ., .], .]
        sage: MAryTree(3, [[], None, None])
        [[., ., .], ., .]
        sage: MAryTree(3, [[], None])
        Traceback (most recent call last):
        ...
        TypeError: this is not a 3-ary tree

    For `m = 2`, the `m`-ary trees are precisely
    the binary trees (:class:`BinaryTree`).
    Sage does distinguish between binary trees
    encoded as instances of :class:`LabelledMAryTree`
    and binary trees encoded as instances of
    :class:`BinaryTree`, but they can be freely
    converted between each other::

        sage: T = LabelledMAryTree(2, [[], []], label=4)
        sage: S = LabelledMAryTree(2, [T, T], label=9); S
        9[4[None[., .], None[., .]], 4[None[., .], None[., .]]]
        sage: parent(S[1][1])
        Labelled 2-ary trees
        sage: X = LabelledBinaryTree(S); X
        9[4[None[., .], None[., .]], 4[None[., .], None[., .]]]
        sage: parent(X[1][1])
        Labelled binary trees
        sage: Y = LabelledMAryTree(2, X); Y
        9[4[None[., .], None[., .]], 4[None[., .], None[., .]]]
        sage: parent(Y[1][1])
        Labelled 2-ary trees
        sage: Y == S
        True
        sage: X == S
        False
        sage: s = MAryTree(2, S); s
        [[[., .], [., .]], [[., .], [., .]]]
        sage: parent(s[1][1])
        2-ary trees
        sage: x = BinaryTree(s); x
        [[[., .], [., .]], [[., .], [., .]]]
        sage: parent(x[1][1])
        Binary trees
        sage: y = MAryTree(2, x); y
        [[[., .], [., .]], [[., .], [., .]]]
        sage: parent(y[1][1])
        2-ary trees
        sage: s == y
        True

    TESTS::

        sage: t = MAryTree(3, [])
        sage: TestSuite(t).run()

    .. SEEALSO::

        :class:`LabelledMAryTree`,
        :class:`BinaryTree`.
    """
    @staticmethod
    def __classcall_private__(cls, *args, **opts):
        r"""
        Ensure that `m`-ary trees created by the enumerated sets and directly
        are the same and that they are instances of :class:`MAryTree`.

        TESTS::

            sage: from sage.combinat.mary_tree import MAryTrees_all
            sage: issubclass(MAryTrees_all(3).element_class, MAryTree)
            True
            sage: t0 = MAryTree(3, [[], None, []])
            sage: t0.parent()
            3-ary trees
            sage: type(t0)
            <class 'sage.combinat.mary_tree.MAryTrees_all_with_category.element_class'>
            sage: t1 = MAryTrees(3)([[], None, []])
            sage: t1.parent() is t0.parent()
            True
            sage: t1 = MAryTrees(3, 3)([[], None, []])
            sage: t1.parent() is t0.parent()
            True
            sage: type(t1) is type(t0)
            True
        """
        m = args[0]
        parent = cls._auto_parent(m)
        args = args[1:]
        return parent.element_class(parent, *args, **opts)

    @staticmethod
    def _auto_parent(m):
        """
        The automatic parent of the element of this class depending on
        the arity.

        When calling the constructor of an element of this class, one needs a
        parent. This class attribute specifies which parent is used.

        INPUT:

        - `m` -- the arity of the tree

        EXAMPLES::

            sage: MAryTree._auto_parent(3)
            3-ary trees
            sage: MAryTree(3, []).parent()
            3-ary trees
        """
        return MAryTrees_all(m)

    def __init__(self, parent, children=None, check=True):
        """
        TESTS::

            sage: MAryTree(3, []).parent()
            3-ary trees
        """
        m = parent.arity()
        if children is None:
            children = []
        elif children == [] or isinstance(children, (Integer, int)):
            children = [None] * m
        if (children.__class__ is self.__class__ and
                children.parent() == parent):
            children = list(children)
        else:
            children = [self.__class__(parent, x) for x in children]
        ClonableArray.__init__(self, parent, children, check=check)

    def arity(self):
        r"""
        Return the arity of the tree.

        EXAMPLES::

            sage: t0 = MAryTree(3, [None, [], []])
            sage: t0.arity()
            3
            sage: t1 = MAryTree(4, [None, [], [], None])
            sage: t1.arity()
            4
        """
        return self.parent().arity()

    def check(self):
        r"""
        Check that ``self`` is an `m`-ary tree.

        EXAMPLES::

            sage: MAryTree(3, [[], [], []]) # indirect doctest
            [[., ., .], [., ., .], [., ., .]]
            sage: MAryTree(3, [[], []])  # indirect doctest
            Traceback (most recent call last):
            ...
            TypeError: this is not a 3-ary tree
            sage: MAryTree(3, [[], [], [], []])       # indirect doctest
            Traceback (most recent call last):
            ...
            TypeError: this is not a 3-ary tree
        """
        if not (not self or len(self) == self.arity()):
            raise TypeError("this is not a %s-ary tree" % (self.arity()))

    def _repr_(self):
        """
        TESTS::

            sage: t1 = MAryTree(3, [None, [], None]); t1  # indirect doctest
            [., [., ., .], .]
            sage: MAryTree(3, [[None, None, []], None, []])  # indirect doctest
            [[., ., [., ., .]], ., [., ., .]]
        """
        if not self:
            return "."
        else:
            return super(MAryTree, self)._repr_()

    def is_empty(self):
        """
        Return whether ``self`` is empty.

        EXAMPLES::

            sage: MAryTree(3).is_empty()
            True
            sage: MAryTree(3, []).is_empty()
            False
            sage: MAryTree(3, [None, [], None]).is_empty()
            False
        """
        return not self

    def canonical_labelling(self, shift=0):
        """
        Return a labelled version of ``self``.

        The actual canonical labelling is currently unspecified. However, it
        is guaranteed to have labels in `1, ..., n` where `n` is the number of
        nodes of the tree. Moreover, two (unlabelled) trees compare as equal if
        and only if their canonical labelled trees compare as equal.

        We use a labelling that generalizes the binary search tree labelling.
        Nodes are labelled in this order:
        ``self[0], root, self[m-1], self[m-2], ..., self[1]``.

        EXAMPLES::

            sage: MAryTree(3).canonical_labelling()
            .
            sage: MAryTree(3, []).canonical_labelling()
            1[., ., .]
            sage: T = MAryTree(3, [[[], None, None], [], [None, [], []]])
            sage: T.canonical_labelling()
            3[2[1[., ., .], ., .], 7[., ., .], 4[., 6[., ., .], 5[., ., .]]]
        """
        LTR = self.parent().labelled_trees()
        if self:
            sz0 = self[0].node_number()
            trees = [self[0].canonical_labelling(shift)]
            shift += sz0 + 1
            label = shift
            otherTrees = []
            for i in range(len(self) - 1, 0, -1):
                child = self[i]
                otherTrees.append(child.canonical_labelling(shift))
                shift += child.node_number()
            otherTrees.reverse()
            trees.extend(otherTrees)
            return LTR(trees, label=label)
        else:
            return LTR(None)

    def unique_growth(self):
        r"""
        This method makes the tree grow in such a way that each tree
        of size `n` is obtained only by growing a unique tree of size
        `n-1`.

        This is used to recursively generate `m`-ary trees. The
        principle of the growth of a tree is to replace a leaf by a node.
        Namely, we only replace leafs that are positioned after
        the last node of the tree in prefix read (:meth:`prefix_read`).

        OUTPUT:

        - an iterator on trees that are obtained by a growth of ``self``

        EXAMPLES::

            sage: t0 = MAryTree(3, [[], [], []]); t0
            [[., ., .], [., ., .], [., ., .]]
            sage: list(t0.unique_growth())
            [[[., ., .], [., ., .], [[., ., .], ., .]], [[., ., .],
            [., ., .], [., [., ., .], .]], [[., ., .], [., ., .],
            [., ., [., ., .]]]]
            sage: t1 = MAryTree(3, [[], None, None]); t1
            [[., ., .], ., .]
            sage: list(t1.unique_growth())
            [[[[., ., .], ., .], ., .], [[., [., ., .], .], ., .],
            [[., ., [., ., .]], ., .], [[., ., .], [., ., .], .],
            [[., ., .], ., [., ., .]]]
            sage: t2 = MAryTree(3, None); t2
            .
            sage: list(t2.unique_growth())
            [[., ., .]]
        """
        # we transform the tree into a word
        word = self.prefix_word()
        # we create the new node we want to add
        node = [0 for i in range(self.arity() + 1)]
        node[0] = 1
        # we find the last node of the tree
        for ind in range(len(word) - 1, -1, -1):
            if(word[ind] == 1):
                break
        else:
            ind = -1
        # for each leaf following the last node, we create a tree
        # where the leaf has been replaced by the new node
        for i in range(ind + 1, len(word)):
            new_word = word[:i]
            new_word.extend(node)
            new_word.extend(word[i + 1:])
            yield(self.parent().from_prefix_word(new_word))

    def prefix_word(self):
        r"""
        Prefix read of the tree.

        We read the tree recursively in this order: ``root``,
        ``self[0]``, ``self[1]``, ..., ``self[m-1]``, and we write 0
        for a leaf and 1 for a node.

        OUTPUT:

        - a list of 0 and 1, where 0 stands for a leaf and 1 for a node

        EXAMPLES::

            sage: t0 = MAryTree(3, [[], [], []]); t0
            [[., ., .], [., ., .], [., ., .]]
            sage: t0.prefix_word()
            [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
            sage: t1 = MAryTree(3, [[], None, None]); t1
            [[., ., .], ., .]
            sage: t1.prefix_word()
            [1, 1, 0, 0, 0, 0, 0]
            sage: t2 = MAryTree(3, [None, [], None]); t2
            [., [., ., .], .]
            sage: t2.prefix_word()
            [1, 0, 1, 0, 0, 0, 0]
        """
        if not self:
            return [0]
        word = [1]
        for t in self:
            word.extend(t.prefix_word())
        return word


# Abstract class to serve as a Factory; no instances are created.
class MAryTrees(UniqueRepresentation, Parent):
    r"""
    Factory class for `m`-ary trees.

    INPUT:

    - `m` -- an integer, the arity of the trees
    - ``size`` -- (optional) an integer, the number of nodes
      in each tree

    OUPUT:

    - the set of all `m`-ary trees (of arity `m` and of the given
      ``size`` if specified)

    EXAMPLES::

        sage: MAryTrees(3)
        3-ary trees
        sage: MAryTrees(3, 2)
        3-ary trees of size 2

    .. NOTE::

        This is a factory class whose constructor returns instances
        of subclasses.
    """
    @staticmethod
    def __classcall_private__(cls, m, n=None):
        """
        TESTS::

            sage: from sage.combinat.mary_tree import MAryTrees_all, MAryTrees_size
            sage: isinstance(MAryTrees(3), MAryTrees)
            True
            sage: isinstance(MAryTrees(3, 2), MAryTrees)
            True
            sage: MAryTrees(3, 3).cardinality()
            12
            sage: MAryTrees(3, 2) is MAryTrees_size(3, 2)
            True
            sage: MAryTrees(3) is MAryTrees_all(3)
            True

        TESTS::

            sage: MAryTrees(-10)
            Traceback (most recent call last):
            ...
            ValueError: m must be a positive integer
        """
        m = Integer(m)
        if not m > 0:
            raise ValueError("m must be a positive integer")
        if n is None:
            return MAryTrees_all(m)
        else:
            n = Integer(n)
            if not n >= 0:
                raise ValueError("n must be a nonnegative integer")
            return MAryTrees_size(m, n)

    @cached_method
    def leaf(self):
        """
        Return a leaf tree with ``self`` as parent.

        EXAMPLES::

            sage: MAryTrees(3).leaf()
            .

        TESTS::

            sage: from sage.combinat.mary_tree import MAryTrees_all
            sage: MAryTrees(3).leaf() is MAryTrees_all(3).leaf()
            True
        """
        return self(None)

    def arity(self):
        r"""
        Return the arity of the trees of the set.

        EXAMPLES::

            sage: MA3 = MAryTrees(3) # indirect doctest
            sage: MA3.arity()
            3
            sage: MA4 = MAryTrees(4) # indirect doctest
            sage: MA4.arity()
            4
            sage: MA3_2 = MAryTrees(3, 2)
            sage: MA3_2.arity()
            3
        """
        return self._m

#################################################################
# Enumerated set of all m-ary trees of a specified arity
#################################################################


class MAryTrees_all(DisjointUnionEnumeratedSets, MAryTrees):

    def __init__(self, m):
        """
        TESTS::

            sage: from sage.combinat.mary_tree import MAryTrees_all
            sage: MA3 = MAryTrees_all(3)
            sage: MA3.cardinality()
            +Infinity

            sage: it = iter(MA3)
            sage: (next(it), next(it), next(it), next(it), next(it))
            (., [., ., .], [[., ., .], ., .], [., [., ., .], .],
            [., ., [., ., .]])
            sage: next(it).parent()
            3-ary trees
            sage: MA3([])
            [., ., .]

            sage: TestSuite(MA3).run()
        """
        self._m = m
        F = Family(NonNegativeIntegers(), self._get_m_ary_trees_size)
        DisjointUnionEnumeratedSets.__init__(self, F,
                                             facade=True, keepkey=False)

    def _get_m_ary_trees_size(self, n):
        r"""
        Return the set of `m`-ary trees of size `n`
        (that is, having `n` nodes).

        EXAMPLES::

            sage: MA3 = MAryTrees(3)  # indirect doctest
            sage: MA3._get_m_ary_trees_size(4)
            3-ary trees of size 4
        """
        return MAryTrees_size(self._m, n)

    def _repr_(self):
        """
        TESTS::

            sage: MA3 = MAryTrees(3); MA3 # indirect doctest
            3-ary trees
        """
        return "%s-ary trees" % (self._m)

    def __contains__(self, x):
        """
        TESTS::

            sage: MA3 = MAryTrees(3) # indirect doctest
            sage: t0 = MA3()
            sage: t0 in MA3
            True
            sage: MA4 = MAryTrees(4) # indirect doctest
            sage: t0 in MA4
            False
            sage: 1 in MA3
            False
        """
        return isinstance(x, self.element_class) and x.arity() == self.arity()

    def __call__(self, x=None, *args, **keywords):
        """
        Ensure that ``None`` instead of ``0`` is passed by default.

        TESTS::

            sage: MA3 = MAryTrees(3)
            sage: MA3()
            .
        """
        return super(MAryTrees, self).__call__(x, *args, **keywords)

    def unlabelled_trees(self):
        """
        Return the set of unlabelled trees associated to ``self``.

        EXAMPLES::

            sage: MAryTrees(3).unlabelled_trees()
            3-ary trees
        """
        return self

    def labelled_trees(self):
        """
        Return the set of labelled trees associated to ``self``.

        EXAMPLES::

            sage: MAryTrees(3).labelled_trees()
            Labelled 3-ary trees
        """
        return LabelledMAryTrees(self._m)

    def _element_constructor_(self, *args, **keywords):
        """
        EXAMPLES::

            sage: MA3 = MAryTrees(3)
            sage: MA3._element_constructor_([])
            [., ., .]
            sage: MA3([[], [], []]) # indirect doctest
            [[., ., .], [., ., .], [., ., .]]
            sage: MA3(None) # indirect doctest
            .
        """
        return self.element_class(self, *args, **keywords)

    def from_prefix_word(self, word, ind=0):
        r"""
        Construct a tree from a list of 0's and 1's, where 0
        stands for a leaf and 1 for a node. The list is supposed
        to be the result of reading the tree in prefix order.

        INPUT:

        - ``word`` -- an list or tuple of 0 and 1
        - ``ind`` -- (default: `0`) the index to start the reading from

        OUTPUT:

        - an `m`-ary tree

        EXAMPLES::

            sage: MA3 = MAryTrees(3)
            sage: MA3.from_prefix_word([1, 0, 0, 1, 0, 0, 0])
            [., ., [., ., .]]
            sage: t0 = MA3([None, [], []])
            sage: t0 == MA3.from_prefix_word(t0.prefix_word())
            True
            sage: MA3.from_prefix_word([1, 0, 0])
            Traceback (most recent call last):
            ...
            ValueError: invalid word
            sage: MA4 = MAryTrees(4)
            sage: MA4.from_prefix_word([1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0])
            [., [., ., ., .], ., [., ., [., ., ., .], .]]
        """
        if len(word) <= ind:
            raise ValueError("invalid word")
        if word[ind] == 0:
            return self()  # empty tree
        ind += 1
        trees = []
        for i in range(self._m):
            tree = self.from_prefix_word(word, ind)
            trees.append(tree)
            ind += tree.node_number() * self._m + 1
        return self(trees)

    Element = MAryTree


#################################################################
# Enumerated set of binary trees of a given size
#################################################################
class MAryTrees_size(MAryTrees):
    """
    The enumerated sets of `m`-ary trees of given size.

    TESTS::

        sage: from sage.combinat.mary_tree import MAryTrees_size
        sage: for i in range(6): TestSuite(MAryTrees_size(3, i)).run()
    """
    def __init__(self, arity, size):
        """
        TESTS::

            sage: MA3_2 = MAryTrees(3, 2)
            sage: MA3_2 == loads(dumps(MA3_2))
            True
            sage: MA3_2 is MAryTrees(3, 2)
            True
        """
        super(MAryTrees_size, self).__init__(category=FiniteEnumeratedSets())
        self._size = size
        self._m = arity

    def __call__(self, x=None, *args, **keywords):
        """
        Ensure that ``None`` instead of ``0`` is passed by default.

        TESTS::

            sage: MA3_2 = MAryTrees(3, 2)
            sage: MA3_2([[], None, None])
            [[., ., .], ., .]
            sage: MA3_0 = MAryTrees(3, 0)
            sage: MA3_0()
            .
            sage: MA3_2()
            Traceback (most recent call last):
            ...
            ValueError: wrong number of nodes

        """
        return super(MAryTrees, self).__call__(x, *args, **keywords)

    def size(self):
        r"""
        Return the size (i.e., the number of nodes) of the
        elements of the set.

        EXAMPLES::

            sage: MA3_2 = MAryTrees(3, 2); MA3_2
            3-ary trees of size 2
            sage: MA3_2.size()
            2
            sage: MA3_3 = MAryTrees(3, 3); MA3_3
            3-ary trees of size 3
            sage: MA3_3.size()
            3
        """
        return self._size

    def _repr_(self):
        """
        TESTS::

            sage: MA3_2 = MAryTrees(3, 2); MA3_2  # indirect doctest
            3-ary trees of size 2

        """
        return "%s-ary trees of size %s" % (self._m, self._size)

    def __contains__(self, x):
        """
        TESTS::

            sage: MA3 = MAryTrees(3)
            sage: MA3_2 = MAryTrees(3, 2)
            sage: 1 in MA3_2
            False
            sage: MA3([[], None, None]) in MA3_2
            True
            sage: MA3([[], [], None]) in MA3_2
            False
            sage: MAryTrees(4)([[], None, None, None]) in MA3_2
            False
        """
        return (isinstance(x, self.element_class) and
                x.node_number() == self._size and
                x.arity() == self._m)

    def _an_element_(self):
        """
        TESTS::

            sage: MAryTrees(3, 2).an_element() # indirect doctest
            [[., ., .], ., .]
        """
        return self.first()

    def cardinality(self):
        r"""
        The cardinality of ``self``

        This is an `m`-Fuss-Catalan number.

        TESTS::

            sage: MAryTrees(3, 0).cardinality()
            1
            sage: MAryTrees(3, 2).cardinality()
            3
            sage: MAryTrees(3, 3).cardinality()
            12
            sage: MAryTrees(4, 3).cardinality()
            22
        """
        n = self._size
        m = self._m - 1
        # we have to force into an Integer otherwise the type is wrong
        return Integer(binomial((m + 1) * n, n) / (m * n + 1))

    def __iter__(self):
        r"""
        Generator using SearchForest and the ``unique_growth``
        method of a tree.

        TESTS::

            sage: MAryTrees(3, 0).list()
            [.]
            sage: MAryTrees(3, 1).list()
            [[., ., .]]
            sage: MAryTrees(3, 2).list()
            [[[., ., .], ., .], [., [., ., .], .], [., ., [., ., .]]]
        """
        if not self._size:
            yield self()
        else:
            roots = MAryTrees(self._m, 0)

            def children(x):
                return x.unique_growth()
            #from sage.combinat.backtrack import SearchForest
            SF = SearchForest(roots, children, algorithm='breadth')
            it = SF.elements_of_depth_iterator(self._size)
            for t in it:
                yield t

    @lazy_attribute
    def _parent_for(self):
        """
        The parent of the element generated by ``self``.

        TESTS::

            sage: MA3_2 = MAryTrees(3, 2)
            sage: MA3_2._parent_for
            3-ary trees
        """
        return MAryTrees_all(self._m)

    @lazy_attribute
    def element_class(self):
        """
        TESTS::

            sage: MA3_2 = MAryTrees(3, 2)
            sage: MA3_2.element_class
            <class 'sage.combinat.mary_tree.MAryTrees_all_with_category.element_class'>
            sage: MA3_2.first().__class__ == MAryTrees(3).first().__class__
            True
        """
        return self._parent_for.element_class

    def _element_constructor_(self, *args, **keywords):
        """
        EXAMPLES::

            sage: MA3_0 = MAryTrees(3, 0)
            sage: MA3_0([])   # indirect doctest
            Traceback (most recent call last):
            ...
            ValueError: wrong number of nodes
            sage: MA3_0()   # indirect doctest
            .

            sage: MA3_1 = MAryTrees(3, 1)   # indirect doctest
            sage: MA3_1([])
            [., ., .]
        """
        res = self.element_class(self._parent_for, *args, **keywords)
        if res.node_number() != self._size:
            raise ValueError("wrong number of nodes")
        return res


@add_metaclass(ClasscallMetaclass)
class LabelledMAryTree(AbstractLabelledClonableTree, MAryTree):
    r"""
    The class of labelled `m`-ary trees.

    A labelled `m`-ary tree (where `m` is a positive integer)
    is a structure that is either a *leaf* or a *node*.
    A leaf carries no information.
    A node is given by a list of `m` labelled `m`-ary trees
    (called its *children*) as well as a label.

    EXAMPLES::

        sage: LMT = LabelledMAryTree
        sage: t1 = LMT(3, [LMT(3, [], label=1), None, None], label=2);t1
        2[1[., ., .], ., .]
    """
    @staticmethod
    def __classcall_private__(cls, *args, **opts):
        """
        Ensure that trees created by the sets and directly are the same and
        that they are instances of :class:`LabelledTree`.

        TESTS::

            sage: LMT = LabelledMAryTree
            sage: issubclass(LabelledMAryTrees(3).element_class, LMT)
            True
            sage: t0 = LabelledMAryTree(3, [None, None, []], label=2)
            sage: t0.parent()
            Labelled 3-ary trees
            sage: type(t0)
            <class 'sage.combinat.mary_tree.LabelledMAryTrees_with_category.element_class'>
        """
        m = args[0]
        parent = cls._auto_parent(m)
        args = args[1:]
        return parent.element_class(parent, *args, **opts)

    @staticmethod
    def _auto_parent(m):
        """
        The automatic parent of the elements of this class.

        When calling the constructor of an element of this class, one needs
        a parent. This class method specifies which parent is used.

        EXAMPLES::

            sage: LabelledMAryTree._auto_parent(3)
            Labelled 3-ary trees
            sage: LabelledMAryTree(3, [], label=1).parent()
            Labelled 3-ary trees
        """
        return LabelledMAryTrees(m)

    def _repr_(self):
        """
        TESTS::

            sage: LMT = LabelledMAryTree
            sage: t1 = LMT(2, [[LMT(2, [], label=2), None], None], label=4); t1
            4[None[2[., .], .], .]
            sage: LMT(2, [[], [[], None]], label = 3)   # indirect doctest
            3[None[., .], None[None[., .], .]]
        """
        if not self:
            if self._label is not None:
                return repr(self._label)
            else:
                return "."
        else:
            return "%s%s" % (self._label, self[:])

    _UnLabelled = MAryTree


class LabelledMAryTrees(LabelledOrderedTrees):
    """
    This is a parent stub to serve as a factory class for trees with
    various labels constraints.
    """
    def __init__(self, m):
        r"""
        TESTS::

            sage: LabelledMAryTrees(3)
            Labelled 3-ary trees
            sage: TestSuite(LabelledMAryTrees(3)).run()
        """
        self._m = m
        LabelledOrderedTrees.__init__(self)

    def arity(self):
        r"""
        Return the arity of the trees of the set.

        EXAMPLES::

            sage: LMA3 = LabelledMAryTrees(3)
            sage: LMA3.arity()
            3
        """
        return self._m

    def _repr_(self):
        """
        TESTS::

            sage: LabelledMAryTrees(3)   # indirect doctest
            Labelled 3-ary trees
        """
        return "Labelled %s-ary trees" % (self._m)

    def _an_element_(self):
        """
        Return a labelled `m`-ary tree.

        EXAMPLES::

            sage: LMA3 = LabelledMAryTrees(3)  # indirect doctest
            sage: LMA3.an_element()
            toto[42[3[., ., .], 3[., ., .], 3[., ., .]], .,
            5[None[., ., .], ., .]]
        """
        LT = self._element_constructor_
        t = LT([], label=3)
        t1 = LT([t] * self._m, label=42)
        t2 = LT([[]] + [None] * (self._m - 1), label=5)
        return LT([t1] + [None] * (self._m - 2) + [t2], label="toto")

    def __call__(self, x=None, *args, **keywords):
        """
        Ensure that ``None`` instead of ``0`` is passed by default.

        TESTS::

            sage: LMA3 = LabelledMAryTrees(3)
            sage: LMA3()
            .
        """
        return super(LabelledOrderedTrees, self).__call__(x, *args, **keywords)

    def unlabelled_trees(self):
        """
        Return the set of unlabelled trees associated to ``self``.

        EXAMPLES::

            sage: LabelledMAryTrees(3).unlabelled_trees()
            3-ary trees

        This is used to compute the shape::

            sage: t = LabelledMAryTrees(3).an_element().shape(); t
            [[[., ., .], [., ., .], [., ., .]], ., [[., ., .], ., .]]
            sage: t.parent()
            3-ary trees

        TESTS::

            sage: t = LabelledMAryTrees(3).an_element()
            sage: t.canonical_labelling()
            5[2[1[., ., .], 4[., ., .], 3[., ., .]], ., 7[6[., ., .], ., .]]
        """
        return MAryTrees_all(self._m)

    def labelled_trees(self):
        """
        Return the set of labelled trees associated to ``self``.

        EXAMPLES::

            sage: LabelledMAryTrees(3).labelled_trees()
            Labelled 3-ary trees
        """
        return self

    Element = LabelledMAryTree