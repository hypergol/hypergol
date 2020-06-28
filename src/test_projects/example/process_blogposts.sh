export PYTHONPATH="${PWD}/..:${PWD}/../..:"

THREADS=4

python3 \
    ./pipelines/process_blogposts.py \
    --threads=${THREADS} \
    $1
