#!/bin/bash

cd ..

if [ ! -d "SymboLinks" ]; then
  git clone https://github.com/SynaLinks/SymboLinks
  cd SymboLinks
  pip3 install .
else
  cd SymboLinks
  git pull
  pip3 install .
fi

cd ..

cd HybridAGI