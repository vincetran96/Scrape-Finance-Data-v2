#!/bin/bash

# Check if input is a number
read -p "enter " inp
if ! [[ "$inp" =~ ^[0-9]+$ ]]; then
    echo "DCM"
else
    echo $inp
fi
