#!/bin/sh
# Historical remote-host example; supply an authorized SSH destination locally.
: "${TOWERSCOUT_SSH_TARGET:?Set TOWERSCOUT_SSH_TARGET to the approved SSH destination}"
ssh -L localhost:8888:localhost:8888 -i "${TOWERSCOUT_SSH_KEY:-towerscout.pem}" "$TOWERSCOUT_SSH_TARGET"
