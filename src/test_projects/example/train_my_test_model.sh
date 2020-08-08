export PYTHONPATH="${PWD}/..:${PWD}/../..:"

python3 \
    ./models/train_my_test_model.py \
    $1
