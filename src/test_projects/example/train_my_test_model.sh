export PYTHONPATH="${PWD}/..:${PWD}/../..:"

python3 \
    ./pipelines/train_my_test_model.py \
    $1
