#!/bin/sh
# Historical model-copy example; supply an authorized SSH destination locally.
: "${TOWERSCOUT_SSH_TARGET:?Set TOWERSCOUT_SSH_TARGET to the approved SSH destination}"
scp -i "${TOWERSCOUT_SSH_KEY:-towerscout.pem}" xl_250_best.pt "${TOWERSCOUT_SSH_TARGET}:xl_250_best.pt"
