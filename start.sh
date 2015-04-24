sudo service mongodb start
sudo python autosnapper/autosnapper.py > autosnaplog.log 2>&1 &

export pythonpid=$!

sudo nodejs snapapprover/app.js > snapapprovelog.log 2>&1 &

export nodepid=$!