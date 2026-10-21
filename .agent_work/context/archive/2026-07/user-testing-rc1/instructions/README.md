# User Testing Instructions

> **ARCHIVED JULY 23, 2026**: Retained for RC1 history only. It is not the
> current Pilot feedback or final-candidate qualification process.

Use this folder for tester-facing reporting instructions. For package-path pilot
testing, start with the UAT guide and RC1 checklist, then use the reporting form
if the tester gets blocked. Normal testers receive the CPU Application Package.
CUDA 12.1 and Podman tracks are support-assigned.

## Setup Guides

- [TowerScout V1 RC1 UAT User Guide](./TowerScout_V1_RC1_UAT_User_Guide.docx)
- [RC1 Pilot / UAT Handoff Packet](./RC1-PILOT-HANDOFF-PACKET.md)
- [RC1 Pilot / UAT Checklist](./RC1-PILOT-UAT-CHECKLIST.md)
- [TowerScout User Testing Guide](../../guides/TowerScout_User_Testing_Guide.txt)
- [TowerScout User Testing Guide - Windows Miniconda](../../guides/TowerScout_User_Testing_Guide_Windows_Miniconda.txt)
- [TowerScout Development Setup Guide](../../guides/TowerScout_Development_Setup_Guide.txt)

## Reporting Form

- [TESTER-ISSUE-REPORT-CHECKLIST.txt](./TESTER-ISSUE-REPORT-CHECKLIST.txt)

## Internal Handoff Rule

Before sending instructions to a tester, fill out the RC1 Pilot / UAT Handoff
Packet with the exact release URL, selected Application Package variant,
artifact filenames, smoke fixture, and support contact.

Once the tester sends the issue report form answers and artifacts:

1. save them into the appropriate `artifacts/` folder
2. update or create the matching `UT-###` issue file
3. update the row in `../issue-tracker.md`
