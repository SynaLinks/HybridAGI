#!/bin/bash

cd ..

if [ ! -d "SymboLinks" ]; then
  git clone https://github.com/SynaLinks/SymboLinks
  cd SymboLinks
  pip3 install --editable .
else
  cd SymboLinks
  git pull
fi

cd ..

cd HybridAGI