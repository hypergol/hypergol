export PYTHONPATH="${PWD}/..:${PWD}/../..:"

python3 \
    ./models/my_test_model/serve_my_test_model.py \
    --port=8000 \
    --host="0.0.0.0"
