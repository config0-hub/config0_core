#!/bin/bash

######################################################
# Functions
######################################################

function run_cmd { 
    cmd="$1"; timeout="$2";
    echo "##########################################"
    echo ""
    echo "executing $cmd"
    echo ""
    echo "##########################################"
    grep -qP '^\d+$' <<< $timeout || timeout=10

    ( 
        eval "$cmd" &
        child=$!
        trap -- "" SIGTERM 
        (       
                sleep $timeout
                echo "---------------------------------------------------------"
                echo "- TIMED_OUT - $cmd"
                echo "---------------------------------------------------------"
                kill $child 2> /dev/null 
                exit 9
                echo "---------------------------------------------------------"
        ) &     
        wait $child
    )
}

function run_docker { 

     export LAMBDA_PKG_NAME=${LAMBDA_PKG_NAME:=test-lambda}
     export LAMBDA_PKG_DIR=${LAMBDA_PKG_DIR:=/var/tmp/packages/lambda}
     export S3_BUCKET=${S3_BUCKET:=test-lambda-bucket}
     export DOCKER_TEMP_IMAGE=${DOCKER_TEMP_IMAGE:=temp-lambda-pkg}
     export WORKING_DIR=${WORKING_DIR:=$WORKING_DIR}
     export WORKING_SUBDIR=${WORKING_SUBDIR:=var/tmp/lambda}

     DOCKER_TEMP_IMAGE="$1"; TIMEOUT="$2";

     echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" > .env
     echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> .env
     echo "LAMBDA_PKG_NAME=${LAMBDA_PKG_NAME}" >> .env
     echo "S3_BUCKET=${S3_BUCKET}" >> .env
     echo "DOCKER_TEMP_IMAGE=${DOCKER_TEMP_IMAGE}" >> .env
     
     #cont=$(docker run -d "$@")
     cont=$(docker run --rm --env-file .env -d $DOCKER_TEMP_IMAGE)
     code=$(timeout "$TIMEOUT" docker wait "$cont" || true)
     docker kill $cont &> /dev/null
     echo -n 'status: '
     if [ -z "$code" ]; then
         echo timeout
     else
         echo exited: $code
     fi
     
     echo output:
     # pipe to sed simply for pretty nice indentation
     docker logs $cont | sed 's/^/\t/'
     docker rm $cont &> /dev/null
}

######################################################
# Main
######################################################
