
Install dependencies:

	sudo npm install -g serverless
    pip install -t vendored -r requirements.txt

Deploy:

    sls deploy -v

    sls deploy function -f rambler
    sls invoke -f rambler -l

    sls invoke local -f rambler
