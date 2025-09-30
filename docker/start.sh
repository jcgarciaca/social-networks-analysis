#! /bin/bash
docker run -it --rm \
    --net="host" \
    --name ssnna \
    -v $(dirname $PWD):/workdir \
    jcgarciaca/ssnna:latest \
    /bin/bash
