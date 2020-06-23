python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install setuptools==47.1.1
pip3 install wheel
pip3 install -r requirements.txt
cd ../../ && pip3 install -e . && cd test_projects/example
python3 -m spacy download en_core_web_sm
