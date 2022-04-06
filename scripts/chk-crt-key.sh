#!/bin/bash

# check-crt-key.sh - check certificate & private key match

set -euf -o pipefail

USAGE="USAGE: chk-crt-key.sh [cert file] [key file]"

OPENSSL=/usr/bin/openssl

if [[ "$#" -ne 2 ]]; then
    echo $USAGE
    exit 1
fi

CERT=$1
KEY=$2

if [[ ! -x $OPENSSL ]]; then
   echo "openssl binary $OPENSSL doesn't exist"
   exit 1
fi

if [[ ! -f "$CERT" ]]; then
   echo "Certificate $CERT doesn't exist"
   echo $USAGE
   exit 1
fi

if [[ ! -f "$KEY" ]]; then
   echo "Key $KEY doesn't exist"
   echo $USAGE
   exit 1
fi

# test key
KEYCHK=$(openssl rsa -check -noout -in "$KEY")
if [[ $KEYCHK != "RSA key ok" ]]; then
   echo "Bad key file $KEY"
   exit 2
fi

CRTMOD=$($OPENSSL x509 -modulus -noout -in "$CERT" | $OPENSSL md5)
KEYMOD=$($OPENSSL rsa -modulus -noout -in "$KEY" | $OPENSSL md5)

if [[ "$KEYMOD" != "$CRTMOD" ]]; then
    echo "Key modulus [$KEYMOD] & Cert modulus [$CRTMOD] don't match"
    exit 3
fi

echo "Key & Cert modulus match"
exit 0
