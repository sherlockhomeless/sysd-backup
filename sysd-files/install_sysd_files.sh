#!/usr/bin/env bash

sudo cp sysd-files/caldav_backup.service /etc/systemd/user
sudo cp sysd-files/caldav_backup.timer /etc/systemd/user

systemctl --user daemon-reload
