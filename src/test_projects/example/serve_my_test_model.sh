export PYTHONPATH="${PWD}/..:${PWD}/../..:"

python3 \
    ./models/serve_my_test_model.py \
    --port=8000 \
    --host="0.0.0.0"
