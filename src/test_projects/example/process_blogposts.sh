
export PYTHONPATH="${PWD}/..:${PWD}/../..:"

THREADS=4

python \
    ./pipelines/process_blogposts.py \
    --threads=${THREADS}
