
export PYTHONPATH="${PWD}/..:${PWD}/../..:"

LOCATION=$1
PROJECT="test"
BRANCH="test1"
SOURCE_PATTERN=$2
THREADS=4

python \
    ./pipelines/process_blogposts.py \
    --location="${LOCATION}" \
    --project="${PROJECT}" \
    --branch="${BRANCH}" \
    --sourcePattern="${SOURCE_PATTERN}" \
    --threads=${THREADS}
