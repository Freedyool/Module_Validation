#外部编译
#借助内核源码中的makefile文件 进行编译

#先指定当前目录
PWD ?= $(shell pwd)

#内核源码路径
KERNELDIR:=/home/yool/dev/tspi_linux_sdk_repo/kernel

obj-m += demo.o

module:
	make -C $(KERNELDIR) M=$(PWD) ARCH=arm64 modules
	@# -C $(KERNELDIR) 从当前目录切换到内核源码下 借助内核源码makefile 进行make
	@# M=$(PWD) 只编译当前目录下的驱动文件
	@# ARCH=arm64 指定编译架构
clean:
	make -C $(KERNELDIR) M=$(PWD) ARCH=arm64 clean