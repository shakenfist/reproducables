import datetime
import errno
import libvirt
import random
import socket
import sys
import time
import uuid


# Enabling this port check makes the VM start correctly. Set this
# to False to see about 10% failures in VM starts.
ENABLE_PORT_CHECK = True


def _port_free(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', port))
        return True
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            print("Port is already in use")
        else:
            print(e)
        return False
    finally:
        s.close()


ALLOCATED = []


def allocate_console_port():
    global ALLOCATED

    port = random.randint(30000, 50000)
    while port in ALLOCATED:
        port = random.randint(30000, 50000)

    if ENABLE_PORT_CHECK:
        while port in ALLOCATED or not _port_free(port):
            port = random.randint(30000, 50000)

    ALLOCATED.append(port)
    return port


def power_on(myxml):
    conn = libvirt.open(None)
    instance = conn.defineXML(myxml)

    try:
        instance.create()
        print('\n%s Instance started correctly' % datetime.datetime.now())
        return True

    except libvirt.libvirtError as e:
        if str(e).find('Failed to find an available port: Address already in use') != -1:
            return False

        if str(e).find('Failed to reserve port') != -1:
            return False

        print('%s libvirt error: %s' % (datetime.datetime.now(), e))
        return False


def run_one():
    xml = """<domain type='kvm'>
  <name>sniffles:%(uuid)s</name>
  <uuid>%(uuid)s</uuid>
  <memory unit='KiB'>1048576</memory>
  <currentMemory unit='KiB'>1048576</currentMemory>
  <vcpu placement='static'>1</vcpu>
  <os>
    <type arch='x86_64' machine='pc-i440fx-2.8'>hvm</type>
    <boot dev='hd'/>
    <boot dev='cdrom'/>
    <bootmenu enable='yes' timeout='3000'/>
  </os>
  <features>
    <acpi/>
    <apic/>
  </features>
  <cpu mode='host-passthrough'>sniffles:%(uuid)s
  </cpu>
  <clock offset='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <pm>
    <suspend-to-mem enabled='no'/>
    <suspend-to-disk enabled='no'/>
  </pm>
  <devices>
    <emulator>/usr/bin/kvm</emulator>

    <serial type='tcp'>
      <source mode='bind' host='0.0.0.0' service='%(serial_port)s'/>
      <protocol type='telnet'/>
      <target port='1'/>
    </serial>

    <graphics type='vnc' port='%(vnc_port)s' listen='0.0.0.0'>
      <listen type='address' address='0.0.0.0'/>
    </graphics>

    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <video>
      <model type='cirrus' vram='16384' heads='1' primary='yes'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </memballoon>
  </devices>
</domain>"""

    myuuid = str(uuid.uuid4())
    serial = allocate_console_port()
    vnc = allocate_console_port()
    myxml = xml % {'uuid': myuuid,
                   'serial_port': serial,
                   'vnc_port': vnc}

    print('%s Starting instance sniffles:%s with serial=%d and vnc=%d'
          % (datetime.datetime.now(), myuuid, serial, vnc))
    attempts = 1

    while not power_on(myxml) and attempts < 100:
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(5)
        attempts += 1

    if attempts == 100:
        print()

    print('%s Finished after %d attempts'
          % (datetime.datetime.now(), attempts))

    return attempts == 1


if __name__ == '__main__':
    fast = 0
    slow = 0

    for i in range(100):
        if run_one():
            fast += 1
        else:
            slow += 1

    print()
    print()
    print('Summary: %d fast and %d slow' % (fast, slow))
