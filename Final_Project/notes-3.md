# Petalinux Large FS Setup (OpenCV)
Normally, petalinux boots from a RAM filesystem which means the entire filesystem must be loaded into RAM, limiting the maximum size of the filesystem and the amount of RAM available. This will separate your rootfs into a separate image file named `rootfs.squashfs`, formatted as a read-only squashed filesystem (see SquashFS). 

A secondary RAM filesystem will boot first, then mount the SD card, then mount the rootfs from the file on the SD card, then boot the rootfs. This allows you to use a large rootfs without partitioning the SD card (which we can't easily do as we do not have root access).

The rootfs type option in `petalinux-config` must stay at the default value of `INITRD`.

First, enter the petalinux kernel menuconfig and enable SquashFS support:
petalinux-config -c kernel
  - File systems
    - Miscellaneous Filesystems
      - SquashFS (Make sure it has a <*>, not <M> at the front, press space to toggle between them)
      - You can disable JFFS2 support, it's just taking up extra space

Second, create/replace a series of files shown below in the petalinux project-spec/meta-user folder:

project-spec/meta-user/conf/petalinuxbsp.conf
```
#User Configuration

#OE_TERMINAL = "tmux"

INITRAMFS_IMAGE = "cpre488-image-fsjump"

IMAGE_FSTYPES_forcevariable = "tar.gz squashfs"
```

project-spec/meta-user/recipes-core/images/cpre488-image-fsjump.bb
```
IMAGE_FSTYPES_forcevariable = "${INITRAMFS_FSTYPES}"

inherit core-image

PACKAGE_INSTALL = " \
  ${VIRTUAL-RUNTIME_base-utils} \
  base-passwd \
  init-fsjump \
  "

# Force petalinux to ignore this image, it's not the real rootfs
python plnx_deploy_rootfs() {
  pass
}
```

project-spec/meta-user/recipes-core/init-fsjump/init-fsjump.bb:
```
SUMMARY = "Init script for jumping to a squashfs stored on the SD Card"
DESCRIPTION = "Init script for jumping to a squashfs stored on the SD Card `/dev/mmcblk0p1` named `rootfs.squashfs`"
SECTION = "base"
LICENSE = "CLOSED"

SRC_URI = "file://init"
S = "${WORKDIR}"

INHIBIT_DEFAULT_DEPS = "1"

do_install () {
	install -m 0755 ${WORKDIR}/init ${D}/init
}

FILES_${PN} = "/init"
```

project-spec/meta-user/recipes-core/init-fsjump/files/init:
```
#!/bin/sh

# Load as little of the system mounts as necessary, we only need /dev and /proc
mount -t devtmpfs devtmpfs /dev
mkdir -p /proc
mount -t proc proc /proc

# Make the two mountpoints
mkdir -p /mnt/sdcard /mnt/rootfs

# Mount the SD card
mount /dev/mmcblk0p1 /mnt/sdcard

# Mount the rootfs from the SD card
mount /mnt/sdcard/rootfs.squashfs /mnt/rootfs

# Move the SD card into the rootfs as /home/root
mount --move /mnt/sdcard /mnt/rootfs/home/root

# And boot the rootfs
exec switch_root /mnt/rootfs /sbin/init
```


That is it!

Build as normal, and make sure you copy image.ub, BOOT.BIN, boot.scr, and rootfs.squashfs onto the sd card.

Note: This also mounts the SD card to /home/root to make your life easier. See below for more tips.


## Notable configurations to make your life easier:

In menuconfig, press / for search to find a package, then the number shown by the package to jump there.

petalinux-config -c rootfs
  - Image Features
    - No ssh-server-dropbear (we have no network, so ssh is useless)
    - Enable auto-login (stop typing root root every boot)
  - Filesystem Packages
    - No console/network/can-utils, net/bridge-utils, misc/tcf-agent, 
    - misc/python3 <= If you really really want to. There are also most python3 packages available to install there as well since pip does not work on the zedboard without internet.
    - libs/opencv, libs/opencv-dev <= libs/opencv is the runtime library, -dev adds headers for compilation on the zedboard **WARNING**: See OpenCV customization below
    - misc/packagegroup-core-buildessential -- GCC, etc for compiling on the zedboard directly for faster build, test cycle time
    - libs/ffmpeg, libs/ffmpeg-dev <= Optional if you want ffmpeg installed

## OpenCV
OpenCV has support for ARM NEON instructions on the Zynq processor, but is not enabled by default:
https://support.xilinx.com/s/question/0D52E00006iHiPVSA0/opencv-neon-optimization-on-petalinux-20191?language=en_US

Create a file with contents below to enable ARM NEON instructions for OpenCV:

project-spec/meta-user/recipes-support/opencv/opencv_%.bbappend:
```
EXTRA_OECMAKE_append_zynq = " -DENABLE_NEON=ON -DENABLE_VFPV3=ON"
```

## Adding kernel headers to the zedboard

For on-device kernel module development, add:
project-spec/meta-user/recipes-core/images/petalinux-image-minimal.bbappend
```
IMAGE_INSTALL_append_zynq = " kernel-devsrc"
```
 - This option is not available in the rootfs menuconfig. And yes, that space is important.
