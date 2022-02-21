export PYTHONPATH="${PWD}/..:${PWD}/../..:"

python3 \
    ./models/my_torch_test_model/train_my_torch_test_model.py \
    $1
