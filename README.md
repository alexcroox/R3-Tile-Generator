# R3-Tile-Generator
AWS Lambda Tile Generator for R3

### Goal
Fast, automated, distributed generation of map tiles for R3 using the parallel computing power of AWS Lambda.

Spawn a single Lambda Instance per required zoom level, upload tiles direct to S3, inform web client of progress through SNS.

### Why not Node.js on Lambda?
Node.js was my initial attempt but every library for image manipulation I tried choked on the ~80MB test PNG files :(

As a result I'm using python and trying my hardest to keep crazy memory usage under control...

### User flow
1. Upload .emf to web interface
2. Wait for completion of automated tile generation...
3. Tiles automatically ready to use in R3 due to S3 remote tile hosting!