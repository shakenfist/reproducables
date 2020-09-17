Sniffles
========

In September 2020, we started experiencing a strange behaviour on Ubuntu 20.04.
As part of launching an instance, we select two random high port numbers -- one
for the serial console and one for the VNC VDI session. We track which ports
we've handed out so we don't double allocate. In September, about 50% of instance
starts started failing in CI because qemu would refuse to bind to the selected
port. It would present this error:

```
Sep 16 08:59:44 cbr-sf-2 WARNING sf-queues-1600246725.2353723-000[2469794] Ignoring instance start error:
internal error: process exited while connecting to monitor: 2020-09-16T08:59:44.110272Z qemu-system-x86_64:
-chardev socket,id=charserial0,host=0.0.0.0,port=39066,telnet,server,nowait,logfile=/dev/fdset/3,logappend=on:
Failed to find an available port: Address already in use; instance=b2f08ea2-5462-4457-9a4e-be06718f0c51;
method=virt.py:513:power_on()
```

I added a check that the selected ports were free, and it didn't help. What did
end up helping was retrying the instance start. It turns out the bind to the port
appears to work after about 60 seconds.

This was happening on three Ubuntu 20.04 machines, all fully patched.

What is this code?
==================

This code is a minimum replication of that problem so I could see if it happens
on other installs of Ubuntu 20.04, or other distros.

Run it like this:

```
sudo apt-get install python3-libvirt
python3 sniffles.py 2> /dev/null
```

This will give you output like this:

```
2020-09-17 01:21:40.241090 Starting instance sniffles:0c6dea7c-8f24-4ecb-8313-06346936267d
............
2020-09-17 01:22:42.743095 Instance started correctly
2020-09-17 01:22:42.743548 Finished after 13 attempts
```

This output means that we tried 13 times to start the instance, with five second
gaps in between. Congratulations, you have the sniffles!