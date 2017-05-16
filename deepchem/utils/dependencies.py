"""
This file is for lazily importing optional dependencies
"""
try:
  import xgboost as xgboost
except:
  print("Warning: No XGBOOST installed on your system")
  print(
      "Attempting to run models with XGBOOST dependencies will throw runtime errors"
  )
  xgboost = None

try:
  import pdbfixer as pdbfixer
except:
  print("Warning: No XGBOOST installed on your system")
  print(
      "Attempting to run models with XGBOOST dependencies will throw runtime errors"
  )
  pdbfixer = None

try:
  import simtk as simtk
except:
  print("Warning: No XGBOOST installed on your system")
  print(
      "Attempting to run models with XGBOOST dependencies will throw runtime errors"
  )
  simtk = None

try:
  import mdtraj as mdtraj
except:
  print("Warning: No XGBOOST installed on your system")
  print(
      "Attempting to run models with XGBOOST dependencies will throw runtime errors"
  )
  mdtraj = None
