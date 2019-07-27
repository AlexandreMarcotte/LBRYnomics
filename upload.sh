#!/usr/bin/expect
spawn sftp ...
expect "password:"
send ...
expect "sftp>"
send "cd public_html/lbrynomics\n"
expect "sftp>"
send "put *.json\n"
expect "sftp>"
send "put *.svg\n"
expect "sftp>"
send "exit\n"
interact
