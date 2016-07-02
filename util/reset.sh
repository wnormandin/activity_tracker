cd $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/..
echo Working in $(pwd)
find . -type f -name *.pyc -ls -delete
if ! [ -z data/activity.db ]; then
    rm data/activity.db
fi
