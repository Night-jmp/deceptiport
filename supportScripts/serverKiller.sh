kill -9 $(ps aux | grep "sudo ./deceptiport" | grep root | awk '{print $2}')
