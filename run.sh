#!/usr/bin/env bash
docker build -t contest-platform .
docker run -d -p 5000:5000 -v data:/opt/data contest-platform