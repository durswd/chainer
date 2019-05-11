import numpy as np
import unittest

from chainer import testing
from chainer.dataset import TabularDataset


class DummyDataset(TabularDataset):

    def __init__(self, mode, callback=None):
        self._mode = mode
        self._callback = callback

        self.data = np.random.uniform(size=(3, 10))

    def __len__(self):
        return self.data.shape[1]

    @property
    def keys(self):
        return ('a', 'b', 'c')

    @property
    def mode(self):
        return self._mode

    def get_examples(self, indices, key_indices):
        if self._callback:
            self._callback(indices, key_indices)

        if indices is None:
            indices = slice(None, None, 1)
        if isinstance(indices, slice):
            start, stop, step = indices.indices(len(self))
            indices = range(start, stop, step)

        if key_indices is None:
            key_indices = (0, 1, 2)

        return tuple(
            list(self.data[key_index, index] for index in indices)
            for key_index in key_indices)


@testing.parameterize(
    {'mode': tuple},
    {'mode': dict},
)
class TestTabularDataset(unittest.TestCase):

    def test_fetch(self):
        def callback(indices, key_indices):
            self.assertIsNone(indices)
            self.assertIsNone(key_indices)

        dataset = DummyDataset(mode=self.mode, callback=callback)

        if self.mode is tuple:
            expected = tuple(list(d) for d in dataset.data)
        elif self.mode is dict:
            expected = dict(zip(
                ('a', 'b', 'c'), (list(d) for d in dataset.data)))

        self.assertEqual(dataset.fetch(), expected)

    def test_get_example(self):
        def callback(indices, key_indices):
            self.assertEqual(indices, [3])
            self.assertIsNone(key_indices)

        dataset = DummyDataset(mode=self.mode, callback=callback)

        if self.mode is tuple:
            expected = tuple(dataset.data[:, 3])
        elif self.mode is dict:
            expected = dict(zip(('a', 'b', 'c'), dataset.data[:, 3]))

        self.assertEqual(dataset.get_example(3), expected)


testing.run_module(__name__, __file__)
