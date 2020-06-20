# clear old files
rm -rf /opt/fad-functions/run/celery/*
rm -rf /opt/fad-functions/logs/*
rm -rf /opt/fad-functions/localData/*

# create workers
celery -A celery_main worker -Q corpAZ -c 8 -n workercorpAZ@%h -l INFO --detach --pidfile="./run/celery/%n.pid"
celery -A celery_main worker -Q finance -c 8 -n workerfinance@%h -l INFO --detach  --pidfile="./run/celery/%n.pid"

# run tasks
python -m celery_run_tasks
