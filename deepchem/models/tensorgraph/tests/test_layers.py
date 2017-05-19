import unittest

import numpy as np
import os
import rdkit
import tensorflow as tf
from nose.tools import assert_true
from tensorflow.python.framework import test_util
from deepchem.feat.mol_graphs import ConvMol
from deepchem.feat.mol_graphs import MultiConvMol
from deepchem.feat.graph_features import ConvMolFeaturizer
from deepchem.models.tensorgraph.layers import Conv1D
from deepchem.models.tensorgraph.layers import Dense
from deepchem.models.tensorgraph.layers import Flatten
from deepchem.models.tensorgraph.layers import Reshape
from deepchem.models.tensorgraph.layers import Transpose
from deepchem.models.tensorgraph.layers import CombineMeanStd
from deepchem.models.tensorgraph.layers import Repeat
from deepchem.models.tensorgraph.layers import GRU
from deepchem.models.tensorgraph.layers import TimeSeriesDense
from deepchem.models.tensorgraph.layers import Input
from deepchem.models.tensorgraph.layers import L2Loss
from deepchem.models.tensorgraph.layers import Concat
from deepchem.models.tensorgraph.layers import Constant
from deepchem.models.tensorgraph.layers import Variable
from deepchem.models.tensorgraph.layers import Add
from deepchem.models.tensorgraph.layers import Multiply
from deepchem.models.tensorgraph.layers import InteratomicL2Distances
from deepchem.models.tensorgraph.layers import SoftMaxCrossEntropy
from deepchem.models.tensorgraph.layers import ReduceMean
from deepchem.models.tensorgraph.layers import ToFloat
from deepchem.models.tensorgraph.layers import ReduceSum
from deepchem.models.tensorgraph.layers import ReduceSquareDifference
from deepchem.models.tensorgraph.layers import Conv2D
from deepchem.models.tensorgraph.layers import MaxPool
from deepchem.models.tensorgraph.layers import InputFifoQueue
from deepchem.models.tensorgraph.layers import GraphConv
from deepchem.models.tensorgraph.layers import GraphPool
from deepchem.models.tensorgraph.layers import GraphGather
from deepchem.models.tensorgraph.layers import BatchNorm
from deepchem.models.tensorgraph.layers import SoftMax
from deepchem.models.tensorgraph.layers import WeightedError
from deepchem.models.tensorgraph.layers import VinaFreeEnergy
from deepchem.models.tensorgraph.layers import WeightedLinearCombo
from deepchem.models.tensorgraph.layers import TensorWrapper

import deepchem as dc


class TestLayers(test_util.TensorFlowTestCase):
  """
  Test that layers function as intended.
  """

  def test_conv_1D(self):
    """Test that Conv1D can be invoked."""
    width = 5
    in_channels = 2
    out_channels = 3
    batch_size = 10
    in_tensor = np.random.rand(batch_size, width, in_channels)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = Conv1D(width, out_channels)(in_tensor)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()

      assert out_tensor.shape == (batch_size, width, out_channels)

  def test_dense(self):
    """Test that Dense can be invoked."""
    in_dim = 2
    out_dim = 3
    batch_size = 10
    in_tensor = np.random.rand(batch_size, in_dim)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = Dense(out_dim)(in_tensor)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, out_dim)

  def test_flatten(self):
    """Test that Flatten can be invoked."""
    in_dim_1 = 2
    in_dim_2 = 2
    out_dim = 4
    batch_size = 10
    in_tensor = np.random.rand(batch_size, in_dim_1, in_dim_2)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = Flatten()(in_tensor)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, out_dim)

  def test_reshape(self):
    """Test that Reshape can be invoked."""
    in_dim_1 = 2
    in_dim_2 = 2
    out_dim = 4
    batch_size = 10
    in_tensor = np.random.rand(batch_size, in_dim_1, in_dim_2)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = Reshape((batch_size, out_dim))(in_tensor)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, out_dim)

  def test_transpose(self):
    """Test that Transpose can be invoked."""
    in_dim_1 = 2
    in_dim_2 = 7
    batch_size = 10
    in_tensor = np.random.rand(batch_size, in_dim_1, in_dim_2)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = Transpose((0, 2, 1))(in_tensor)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, in_dim_2, in_dim_1)

  def test_combine_mean_std(self):
    """Test that Transpose can be invoked."""
    dim = 2
    batch_size = 10
    mean_tensor = np.random.rand(dim)
    std_tensor = np.random.rand(
        1,)
    with self.test_session() as sess:
      mean_tensor = tf.convert_to_tensor(mean_tensor, dtype=tf.float32)
      std_tensor = tf.convert_to_tensor(std_tensor, dtype=tf.float32)
      out_tensor = CombineMeanStd()(mean_tensor, std_tensor)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (dim,)

  def test_repeat(self):
    """Test that Repeat can be invoked."""
    in_dim = 4
    batch_size = 10
    n_repeat = 2
    in_tensor = np.random.rand(batch_size, in_dim)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = Repeat(n_repeat)(in_tensor)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, n_repeat, in_dim)

  def test_gru(self):
    """Test that GRU can be invoked."""
    batch_size = 10
    n_hidden = 7
    in_channels = 4
    out_channels = 5
    n_repeat = 2
    n_steps = 6
    in_tensor = np.random.rand(batch_size, n_steps, in_channels)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = GRU(n_hidden, out_channels, batch_size)(in_tensor)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, n_steps, out_channels)

  def test_time_series_dense(self):
    """Test that TimeSeriesDense can be invoked."""
    batch_size = 10
    n_hidden = 7
    in_channels = 4
    out_channels = 5
    n_repeat = 2
    n_steps = 6
    in_tensor = np.random.rand(batch_size, n_steps, in_channels)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = TimeSeriesDense(out_channels)(in_tensor)
      assert out_tensor.shape == (batch_size, n_steps, out_channels)

  def test_input(self):
    """Test that Input can be invoked."""
    in_shape = (4, 3)
    with self.test_session() as sess:
      out_tensor = Input(in_shape)()

  def test_l2_loss(self):
    """Test that L2Loss can be invoked."""
    batch_size = 10
    n_features = 5
    guess_tensor = np.random.rand(batch_size, n_features)
    label_tensor = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      guess_tensor = tf.convert_to_tensor(guess_tensor, dtype=tf.float32)
      label_tensor = tf.convert_to_tensor(label_tensor, dtype=tf.float32)
      out_tensor = L2Loss()(guess_tensor, label_tensor)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size,)

  def test_softmax(self):
    """Test that Softmax can be invoked."""
    batch_size = 10
    n_features = 5
    in_tensor = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = SoftMax()(in_tensor)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, n_features)

  def test_concat(self):
    """Test that Concat can be invoked."""
    batch_size = 10
    n_features = 5
    in_tensor_1 = np.random.rand(batch_size, n_features)
    in_tensor_2 = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      in_tensor_1 = tf.convert_to_tensor(in_tensor_1, dtype=tf.float32)
      in_tensor_2 = tf.convert_to_tensor(in_tensor_2, dtype=tf.float32)
      out_tensor = Concat(axis=1)(in_tensor_1, in_tensor_2)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, 2 * n_features)

  def test_constant(self):
    """Test that Constant can be invoked."""
    value = np.random.uniform(size=(2, 3)).astype(np.float32)
    with self.test_session() as sess:
      out_tensor = Constant(value)()
      assert np.array_equal(value, out_tensor.eval())

  def test_variable(self):
    """Test that Variable can be invoked."""
    value = np.random.uniform(size=(2, 3)).astype(np.float32)
    with self.test_session() as sess:
      out_tensor = Variable(value)()
      sess.run(tf.global_variables_initializer())
      assert np.array_equal(value, out_tensor.eval())

  def test_add(self):
    """Test that Add can be invoked."""
    value1 = np.random.uniform(size=(2, 3)).astype(np.float32)
    value2 = np.random.uniform(size=(2, 3)).astype(np.float32)
    value3 = np.random.uniform(size=(2, 3)).astype(np.float32)
    with self.test_session() as sess:
      out_tensor = Add(weights=[1, 2, 1])(
          tf.constant(value1), tf.constant(value2), tf.constant(value3))
      assert np.array_equal(value1 + 2 * value2 + value3, out_tensor.eval())

  def test_multiply(self):
    """Test that Multiply can be invoked."""
    value1 = np.random.uniform(size=(2, 3)).astype(np.float32)
    value2 = np.random.uniform(size=(2, 3)).astype(np.float32)
    value3 = np.random.uniform(size=(2, 3)).astype(np.float32)
    with self.test_session() as sess:
      out_tensor = Multiply()(tf.constant(value1), tf.constant(value2),
                              tf.constant(value3))
      assert np.array_equal(value1 * value2 * value3, out_tensor.eval())

  def test_interatomic_distances(self):
    """Test that the interatomic distance calculation works."""
    N_atoms = 5
    M_nbrs = 2
    ndim = 3

    with self.test_session() as sess:
      coords = np.random.rand(N_atoms, ndim)
      nbr_list = np.random.randint(0, N_atoms, size=(N_atoms, M_nbrs))

      coords_tensor = tf.convert_to_tensor(coords)
      nbr_list_tensor = tf.convert_to_tensor(nbr_list)

      dist_tensor = InteratomicL2Distances(N_atoms, M_nbrs, ndim)(
          coords_tensor, nbr_list_tensor)

      dists = dist_tensor.eval()
      assert dists.shape == (N_atoms, M_nbrs)

  def test_softmax_cross_entropy(self):
    """Test that SoftMaxCrossEntropy can be invoked."""
    batch_size = 10
    n_features = 5
    logit_tensor = np.random.rand(batch_size, n_features)
    label_tensor = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      logit_tensor = tf.convert_to_tensor(logit_tensor, dtype=tf.float32)
      label_tensor = tf.convert_to_tensor(label_tensor, dtype=tf.float32)
      out_tensor = SoftMaxCrossEntropy()(logit_tensor, label_tensor)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, 1)

  def test_reduce_mean(self):
    """Test that ReduceMean can be invoked."""
    batch_size = 10
    n_features = 5
    in_tensor = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = ReduceMean()(in_tensor)
      out_tensor = out_tensor.eval()
      assert isinstance(out_tensor, np.float32)

  def test_to_float(self):
    """Test that ToFloat can be invoked."""
    batch_size = 10
    n_features = 5
    in_tensor = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = ToFloat()(in_tensor)
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, n_features)

  def test_reduce_sum(self):
    """Test that ReduceSum can be invoked."""
    batch_size = 10
    n_features = 5
    in_tensor = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = ReduceSum()(in_tensor)
      out_tensor = out_tensor.eval()
      assert isinstance(out_tensor, np.float32)

  def test_reduce_square_difference(self):
    """Test that ReduceSquareDifference can be invoked."""
    batch_size = 10
    n_features = 5
    in_tensor_1 = np.random.rand(batch_size, n_features)
    in_tensor_2 = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      in_tensor_1 = tf.convert_to_tensor(in_tensor_1, dtype=tf.float32)
      in_tensor_2 = tf.convert_to_tensor(in_tensor_2, dtype=tf.float32)
      out_tensor = ReduceSquareDifference()(in_tensor_1, in_tensor_2)
      out_tensor = out_tensor.eval()
      assert isinstance(out_tensor, np.float32)

  def test_conv_2D(self):
    """Test that Conv2D can be invoked."""
    length = 4
    width = 5
    in_channels = 2
    out_channels = 3
    batch_size = 20
    in_tensor = np.random.rand(batch_size, length, width, in_channels)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = Conv2D(out_channels, kernel_size=1)(in_tensor)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, length, width, out_channels)

  def test_max_pool(self):
    """Test that MaxPool can be invoked."""
    length = 2
    width = 2
    in_channels = 2
    batch_size = 20
    in_tensor = np.random.rand(batch_size, length, width, in_channels)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = MaxPool()(in_tensor)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, 1, 1, in_channels)

  def test_input_fifo_queue(self):
    """Test InputFifoQueue can be invoked."""
    batch_size = 10
    n_features = 5
    in_tensor = np.random.rand(batch_size, n_features)
    tf.reset_default_graph()
    with self.test_session() as sess:
      in_tensor = TensorWrapper(
          tf.convert_to_tensor(in_tensor, dtype=tf.float32), name="input")
      InputFifoQueue([(batch_size, n_features)], ["input"])(in_tensor)

  def test_graph_conv(self):
    """Test that GraphConv can be invoked."""
    out_channels = 2
    n_atoms = 4  # In CCC and C, there are 4 atoms
    raw_smiles = ['CCC', 'C']
    mols = [rdkit.Chem.MolFromSmiles(s) for s in raw_smiles]
    featurizer = ConvMolFeaturizer()
    mols = featurizer.featurize(mols)
    multi_mol = ConvMol.agglomerate_mols(mols)
    atom_features = multi_mol.get_atom_features()
    degree_slice = multi_mol.deg_slice
    membership = multi_mol.membership
    deg_adjs = multi_mol.get_deg_adjacency_lists()[1:]

    with self.test_session() as sess:
      atom_features = tf.convert_to_tensor(atom_features, dtype=tf.float32)
      degree_slice = tf.convert_to_tensor(degree_slice, dtype=tf.int32)
      membership = tf.convert_to_tensor(membership, dtype=tf.int32)
      deg_adjs_tf = []
      for deg_adj in deg_adjs:
        deg_adjs_tf.append(tf.convert_to_tensor(deg_adj, dtype=tf.int32))
      args = [atom_features, degree_slice, membership] + deg_adjs_tf
      out_tensor = GraphConv(out_channels)(*args)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (n_atoms, out_channels)

  # TODO(rbharath): This test should pass. Fix it!
  #def test_graph_pool(self):
  #  """Test that GraphPool can be invoked."""
  #  out_channels = 2
  #  n_atoms = 4 # In CCC and C, there are 4 atoms
  #  raw_smiles = ['CCC', 'C']
  #  mols = [rdkit.Chem.MolFromSmiles(s) for s in raw_smiles]
  #  featurizer = ConvMolFeaturizer()
  #  mols = featurizer.featurize(mols)
  #  multi_mol = ConvMol.agglomerate_mols(mols)
  #  atom_features = multi_mol.get_atom_features()
  #  degree_slice = multi_mol.deg_slice
  #  membership = multi_mol.membership
  #  deg_adjs = multi_mol.get_deg_adjacency_lists()[1:]

  #  with self.test_session() as sess:
  #    atom_features = tf.convert_to_tensor(atom_features, dtype=tf.float32)
  #    degree_slice = tf.convert_to_tensor(degree_slice, dtype=tf.int32)
  #    membership = tf.convert_to_tensor(membership, dtype=tf.int32)
  #    deg_adjs_tf = []
  #    for deg_adj in deg_adjs:
  #      deg_adjs_tf.append(tf.convert_to_tensor(deg_adj, dtype=tf.int32))
  #    args = [atom_features, degree_slice, membership] + deg_adjs_tf
  #    out_tensor = GraphPool(out_channels)(*args)
  #    sess.run(tf.global_variables_initializer())
  #    out_tensor = out_tensor.eval()
  #    assert out_tensor.shape == (n_atoms, out_channels)

  def test_graph_gather(self):
    """Test that GraphGather can be invoked."""
    batch_size = 2
    n_features = 75
    n_atoms = 4  # In CCC and C, there are 4 atoms
    raw_smiles = ['CCC', 'C']
    mols = [rdkit.Chem.MolFromSmiles(s) for s in raw_smiles]
    featurizer = ConvMolFeaturizer()
    mols = featurizer.featurize(mols)
    multi_mol = ConvMol.agglomerate_mols(mols)
    atom_features = multi_mol.get_atom_features()
    degree_slice = multi_mol.deg_slice
    membership = multi_mol.membership
    deg_adjs = multi_mol.get_deg_adjacency_lists()[1:]

    with self.test_session() as sess:
      atom_features = tf.convert_to_tensor(atom_features, dtype=tf.float32)
      degree_slice = tf.convert_to_tensor(degree_slice, dtype=tf.int32)
      membership = tf.convert_to_tensor(membership, dtype=tf.int32)
      deg_adjs_tf = []
      for deg_adj in deg_adjs:
        deg_adjs_tf.append(tf.convert_to_tensor(deg_adj, dtype=tf.int32))
      args = [atom_features, degree_slice, membership] + deg_adjs_tf
      out_tensor = GraphGather(batch_size)(*args)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()
      # TODO(rbharath): Why is it 2*n_features instead of n_features?
      assert out_tensor.shape == (batch_size, 2 * n_features)

  def test_batch_norm(self):
    """Test that BatchNorm can be invoked."""
    batch_size = 10
    n_features = 5
    in_tensor = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      in_tensor = tf.convert_to_tensor(in_tensor, dtype=tf.float32)
      out_tensor = BatchNorm()(in_tensor)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, n_features)

  def test_weighted_error(self):
    """Test that WeightedError can be invoked."""
    batch_size = 10
    n_features = 5
    guess_tensor = np.random.rand(batch_size, n_features)
    label_tensor = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      guess_tensor = tf.convert_to_tensor(guess_tensor, dtype=tf.float32)
      label_tensor = tf.convert_to_tensor(label_tensor, dtype=tf.float32)
      out_tensor = WeightedError()(guess_tensor, label_tensor)
      out_tensor = out_tensor.eval()
      assert isinstance(out_tensor, np.float32)

  def test_vina_free_energy(self):
    """Test that VinaFreeEnergy can be invoked."""
    n_atoms = 5
    m_nbrs = 1
    ndim = 3
    nbr_cutoff = 1
    start = 0
    stop = 4
    X_tensor = np.random.rand(n_atoms, ndim)
    Z_tensor = np.random.randint(0, 2, (n_atoms))
    with self.test_session() as sess:
      X_tensor = tf.convert_to_tensor(X_tensor, dtype=tf.float32)
      Z_tensor = tf.convert_to_tensor(Z_tensor, dtype=tf.float32)
      out_tensor = VinaFreeEnergy(n_atoms, m_nbrs, ndim, nbr_cutoff, start,
                                  stop)(X_tensor, Z_tensor)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()
      assert isinstance(out_tensor, np.float32)

  def test_weighted_linear_combo(self):
    """Test that WeightedLinearCombo can be invoked."""
    batch_size = 10
    n_features = 5
    in_tensor_1 = np.random.rand(batch_size, n_features)
    in_tensor_2 = np.random.rand(batch_size, n_features)
    with self.test_session() as sess:
      in_tensor_1 = tf.convert_to_tensor(in_tensor_1, dtype=tf.float32)
      in_tensor_2 = tf.convert_to_tensor(in_tensor_2, dtype=tf.float32)
      out_tensor = WeightedLinearCombo()(in_tensor_1, in_tensor_2)
      sess.run(tf.global_variables_initializer())
      out_tensor = out_tensor.eval()
      assert out_tensor.shape == (batch_size, n_features)
