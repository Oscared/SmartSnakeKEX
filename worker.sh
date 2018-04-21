#!/bin/bash

echo "Fixed size:"
python3 snake_agent.py -o models/0419.d.mod -t -r -v
echo "Incrementing size"
python3 snake_agent.py -o models/0419.i.mod -t -r -v -i

