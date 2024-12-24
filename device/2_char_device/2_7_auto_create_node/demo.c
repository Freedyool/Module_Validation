#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/io.h>#include <linux/uaccess.h>#include <linux/device.h>#define MY_NAME "chardev"
#define PMU_GRF_GPIO0B_IOMUX_H  0xFDC2000C#define GPIO_SWPORT_DDR_L 0xFE760008#define GPIO_SWPORT_DR_L 0xFE760000int major = 0;
char kbuf[32] = {0};unsigned int *virt_iomux;unsigned int *virt_ddr;unsigned int *virt_dr;struct class * cls = NULL;struct device *dev = NULL;int my_open (struct inode *inode, struct file *file)
{
	printk("open!\n");
	return 0;
}
ssize_t my_read (struct file *file, char __user *ubuf, size_t size, loff_t *offset)
{
	printk("read!\n");
	return 0;
}
ssize_t my_write (struct file *file, const char __user *ubuf, size_t size, loff_t *offset)
{
	printk("write!\n");
	if(size > sizeof(kbuf)) size = sizeof(kbuf);	if(copy_from_user(kbuf,ubuf,size))	{		printk("copy data from user fail!\n");		return -EIO;	}	if(kbuf[0] == '1')	{		*virt_dr = (1 << 28) | (1 << 12);//输出为高电平	}	return size;
}
int my_close (struct inode *inode, struct file *file)
{
	printk("close!\n");
	return 0;
}

struct file_operations fops = {
	.open = my_open,
	.read = my_read,
	.write = my_write,
	.release = my_close
};
int my_led_init(void){	//复用功能寄存器	virt_iomux = ioremap(PMU_GRF_GPIO0B_IOMUX_H,4);	if(virt_iomux == NULL)	{		printk("ioremap iomux register error !\n");		return -ENOMEM;	}	//方向寄存器	virt_ddr = ioremap(GPIO_SWPORT_DDR_L,4);	if(virt_ddr == NULL)	{		printk("ioremap ddr register error !\n");		return -ENOMEM;	}	//数据寄存器
	virt_dr = ioremap(GPIO_SWPORT_DR_L,4);	if(virt_dr == NULL)	{		printk("ioremap dr register error !\n");		return -ENOMEM;	}	*virt_iomux &= 0xFFFFFFF8; //0-2位清零 设置为gpio模式    //*virt_ddr |= (1<<29); //29位置1 设置写使能	*virt_ddr |= (1<<12 | 1<<28); //12位置1 设置为输出模式 28位置1 设置写使能(10001000)	*virt_dr = (*virt_dr | (1 <<28)) | (*virt_dr & 0xFFFFEFFF); //29位置1 设置写使能 13位清零  设置为低电平	return 0;}static int __init mycdev_init(void)
{	
	major = register_chrdev(0, MY_NAME, &fops);
	if(major < 0)
	{
		printk("reg failed!\n");
		return -1;
	}
	printk("reg successed\n");
	my_led_init();	cls = class_create(THIS_MODULE,"hi");	if(IS_ERR(cls))	{		printk("class create failed!\n");		return PTR_ERR(cls);	}	dev = device_create(cls,NULL,MKDEV(major,0),NULL,"test");	if(IS_ERR(dev))	{		printk("device create failed!\n");		return PTR_ERR(dev);	}    return 0;
}
int my_led_deinit(void){	*virt_dr = (*virt_dr | (1<<28)  | (*virt_dr & 0xFFFFEFFF));	iounmap(virt_iomux);	iounmap(virt_dr);	iounmap(virt_ddr);	return 0;}
static void __exit mycdev_exit(void)
{
	device_destroy(cls,MKDEV(major,0));	class_destroy(cls);	my_led_deinit();	printk("hello world %s\n","exit");
	unregister_chrdev(major, MY_NAME);
}

module_init(mycdev_init);

module_exit(mycdev_exit);

MODULE_LICENSE("GPL");MODULE_AUTHOR("LiSir LiSir@qq.com");
