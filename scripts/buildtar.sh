#!/bin/bash -x

# buildtar.sh - build a tar from git repo
# needs 2 env vars: $GITURL & $DIR (subdir inside repo)

ORIGDIR=$PWD

# source keychain ssh-agent if exists
for kc in $(ls ~/.keychain/*-sh)
do
    . $kc
done

MYTMPDIR=/tmp/buildtar.$$
mkdir $MYTMPDIR

trap 'rm -rf $MYTMPDIR' EXIT

if [ -n $GITURL -o -n $DIR ]; then
    cd $MYTMPDIR
    git clone $GITURL
    cd $(basename $GITURL | sed -e 's/.git//')/$DIR/..
    filename=$(basename $DIR)
    tar cvf $MYTMPDIR/$filename.tar $filename
    mv $MYTMPDIR/$filename.tar $ORIGDIR
else
    echo "GITURL & DIR env vars must be set"
fi

exit

