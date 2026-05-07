# LFDAQINGESTER

## Introduction

`LFDAQIngester` is a containerized python application meant for use in the large `DAQ-service` as a part of the _[Buckeye Space Launch Initiative Liquid Rocket Systems Test Stand Software Stack]()_ (what a mouthful). This pulls raw data from a LabJack T7 pro, calibrates that data, and writes that data to a Quest DB database. The information for which LabJack ports to query and how to calibrate the resulting data is grabbed on program start.

## Guide to the repo:
- Information on tests can be found in `testing.md`
- Information on system architecture can be found in `architecture.md`
- Information on pending development tasks and their status can be found in `TODO.md`
- All code can be found in `/src`

## Build Instructions

To build the image locally, run the following while in the project root:

```
docker build .
```

To the run the image locally and check for errors, run

```
docker compose up
```

Environment variables for the database url and the update delay are stored in `compose.yaml`.



