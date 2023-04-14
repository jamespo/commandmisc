#!/bin/bash

# acme-renewhook.sh - run as acme.sh le_renewhook
# USAGE: acme-renewhook.sh DOMAIN [service to restart]

ROOTDIR=/root/.acme.sh

DOMAIN=$1
SERVICE_TO_RESTART=$2

if [[ $DOMAIN == "" ]]; then
    echo No domain specified
    exit 1
fi

FULLDIR=$ROOTDIR/$DOMAIN
TARGETDIR=/etc/certs/$DOMAIN

cd $FULLDIR || exit 1

mkdir -p $TARGETDIR 2>/dev/null

cp $FULLDIR/$DOMAIN.cer $TARGETDIR
cp $FULLDIR/$DOMAIN.key $TARGETDIR
cp $FULLDIR/fullchain.cer $TARGETDIR

if [[ $SERVICE_TO_RESTART != "" ]]; then
    systemctl restart $SERVICE_TO_RESTART
fi

exit 0

