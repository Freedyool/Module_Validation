#外部编译
#借助内核源码中的makefile文件 进行编译

#先指定当前目录
PWD ?= $(shell pwd)

#内核源码路径
KERNELDIR:=/home/yool/dev/tspi_linux_sdk_repo/kernel
CROSS_COMPILE ?= /home/yool/dev/tspi_linux_sdk_repo/prebuilts/gcc/linux-x86/aarch64/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-

obj-m += demo.o

CC := $(CROSS_COMPILE)gcc

module:
	make -C $(KERNELDIR) M=$(PWD) ARCH=arm64 modules
	@# -C $(KERNELDIR) 从当前目录切换到内核源码下 借助内核源码makefile 进行make
	@# M=$(PWD) 只编译当前目录下的驱动文件
	@# ARCH=arm64 指定编译架构
	$(CC) test.c -o test
clean:
	make -C $(KERNELDIR) M=$(PWD) ARCH=arm64 clean
	rm -rf test
