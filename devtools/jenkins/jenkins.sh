#!/usr/bin/env bash
envname=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1`
bash scripts/install_deepchem_conda.sh $envname
source activate $envname
python setup.py install

rm examples/results.csv || true
cd examples
python benchmark.py -d tox21
export retval1=$?

cd ..
nosetests -v devtools/jenkins/compare_results.py --with-xunit || true
export retval2=$?
nosetests -a 'slow' --with-timer deepchem --with-xunit -unit-file=slow_tests.xml|| true
export retval3=$?

source deactivate
conda remove --name $envname --all
export retval=$(($retval1 + $retval2 + $retval3))
exit ${retval}
