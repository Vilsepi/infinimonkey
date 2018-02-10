
Prerequisites:

- Python 3.6
- npm (for installing Serverless Framework)

If you have problems with Python 2/3, you can create a virtualenv:

    cd ../tools/
    virtualenv -p python3.6 monkey-venv
    source monkey-venv/bin/activate

Install dependencies:

    sudo npm install -g serverless
    pip3 install -U -t vendored -r requirements.txt

    npm install --save-dev serverless-plugin-tracing

Deploy:

    sls deploy -v

    sls deploy function -f rambler
    sls invoke -f rambler -l

    sls invoke local -f rambler
