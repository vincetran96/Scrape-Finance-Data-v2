#!/bin/bash
# This is just a test script

# Check if input is a number
read -p "enter " inp
if ! [[ "$inp" =~ ^[0-9]+$ ]]; then
    echo "DCM"
else
    echo $inp
fi

# Run scripts/functions in parallel
func_one () {
    sleep $inp
    echo "yeah one"
}

func_two () {
    sleep $inp
    echo "yeah two"
}

func_one & PIDONE=$!
func_two & PIDTWO=$!
wait $PIDONE
wait $PIDTWO
