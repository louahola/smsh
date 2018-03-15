# smsh
A command line tool for allowing interactive SSH-like access via SSM SendCommand.

## installing
Currently, `smsh` is only distributed as source. Clone this repository and then bulid it with setuptools:

```
python setup.py install
```

## usage
`smsh` allows you to enter a shell session by just providing the instance-id or IP address:

```
smsh i-123450asdf12345
```

Once "connected", the user is then given an input prompt, similar to a shell prompt:

```
[root@demo-instance root]#
```

The instance name will get set to the "Name" tag of the instance, or will default to the instance-id if no Name is set.
The user can then interact with the session like it was a remote shell:

```
[root@demo-instance root]# ls -al
total 40
dr-xr-x---  3 root root 4096 Mar 15 21:47 .
dr-xr-xr-x 25 root root 4096 Mar 15 18:44 ..
-rw-r--r--  1 root root   18 Jan 15  2011 .bash_logout
-rw-r--r--  1 root root  176 Jan 15  2011 .bash_profile
-rw-r--r--  1 root root  176 Jan 15  2011 .bashrc
-rw-r--r--  1 root root  100 Jan 15  2011 .cshrc
drwx------  2 root root 4096 Mar 14 21:53 .ssh
-rw-r--r--  1 root root  129 Jan 15  2011 .tcshrc
[root@demo-instance root]#
```

### output
This tool supports unbuffered output mode (still technically buffered), where users can get constant real time
output for long-running commands. This is a large limitation of SSM. By default, all output is unbuffered. This
can lead to performance issues though, as the client will be constantly polling the instance for the latest output.
Clients can run in buffered mode by adding the argument, `--buffered-output`.

Because there is near real-time output, long running commands are fully supported. Additionally, things like `tail -f`
are natively supported.

```
[root@demo-instance root]# tail -f my.log
long running process Thu Mar 15 21:51:02 UTC 2018!!!!
long running process Thu Mar 15 21:51:03 UTC 2018!!!!
long running process Thu Mar 15 21:51:04 UTC 2018!!!!
long running process Thu Mar 15 21:51:05 UTC 2018!!!!
long running process Thu Mar 15 21:51:06 UTC 2018!!!!
long running process Thu Mar 15 21:51:07 UTC 2018!!!!
long running process Thu Mar 15 21:51:08 UTC 2018!!!!
long running process Thu Mar 15 21:51:09 UTC 2018!!!!
long running process Thu Mar 15 21:51:10 UTC 2018!!!!
long running process Thu Mar 15 21:51:11 UTC 2018!!!!

```


### state
The session state is maintained throughout the session. This includes the current working directory, the current environment
variables (both local and exported), and the current user.

```
root@demo-instance root]# pwd
/root
[root@demo-instance root]# cd /var/log
[root@demo-instance log]# pwd
/var/log
[root@demo-instance log]#
```

### editor
This tool also allows for local Vi/Nano editors to be used. Just like when normally using them on a remote machine,
they can open up existing or new files. However, because of the nature of the program, any new files that are opened
in an editor and saved without any content are discarded.

```
[root@demo-instance log]# vi somefile.txt
```


## considerations
The following are some considerations for using this tool:

* This tool polls a lot. If there are many users in an account,
  or if there are many commands being executed, API calls
  could be throttled.
* DescribeCommandInvocation does not support tag based permissions. So,
  while you can control the SendCommand based on tag,
  anyone will effectively be able to see the output of every command.
* SSM limits the script size that can be sent via the SendCommand
  action. This size limit can impact the Editor usage, when editing
  very large files.
* Output buffering. Even the unbuffered mode buffers 100 lines at a time.
  If the output is happening faster than that, the command can get backed up.
