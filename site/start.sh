#!/bin/bash
uwsgi -s /tmp/website.sock --manage-script-name --mount /website=server:app --enable-threads