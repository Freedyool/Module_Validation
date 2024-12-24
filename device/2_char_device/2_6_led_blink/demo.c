#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/io.h>#include <linux/uaccess.h>#define MY_NAME "chardev"
#define PMU_GRF_GPIO3B_IOMUX_H 0xFDC6004C#define GPIO_SWPORT_DDR_L 0xFE760008#define GPIO_SWPORT_DR_L 0xFE760000int major = 0;
char kbuf[128] = {0};
unsigned int *virt_iomux;unsigned int *virt_ddr;unsigned int *virt_dr;int my_open (struct inode *inode, struct file *file)
{
	printk("open!\n");
	return 0;
}
ssize_t my_read (struct file *file, char __user *ubuf, size_t size, loff_t *offset)
{
	if(size > sizeof(kbuf)) size = sizeof(kbuf);	if(copy_to_user(ubuf,kbuf,size))	{		printk("copy data to user fail!\n");		return -EIO;	}	return size;
}
ssize_t my_write (struct file *file, const char __user *ubuf, size_t size, loff_t *offset)
{
	if(size > sizeof(kbuf)) size = sizeof(kbuf);	if(copy_from_user(kbuf,ubuf,size))	{		printk("copy data form user fail!\n");		return -EIO;	}	if(kbuf[0] == '1')	{		//0xFE760000 12位写1（设置输出高电平）  28位写1（写使能)		*virt_dr |= 0x10001000;	}	return size;}
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
int my_led_init(void){	virt_iomux = ioremap(PMU_GRF_GPIO3B_IOMUX_H, 4);	if(virt_iomux == NULL)	{		printk("ioremap iomux register error! \n");		return -ENOMEM;	}	virt_ddr = ioremap(GPIO_SWPORT_DDR_L, 4);	if(virt_ddr == NULL)	{		printk("ioremap ddr register error! \n");		return -ENOMEM;	}		virt_dr = ioremap(GPIO_SWPORT_DR_L, 4);	if(virt_dr == NULL)	{		printk("ioremap dr register error! \n");		return -ENOMEM;	}	//0xFDC6004C 0-2位写0（gpio功能）	  16-18 写1（写使能）	*virt_iomux |= 0x70000;	//0xFE760008   12位写1（设置为输出）  28位写1（写使能）	*virt_ddr |= 0x10001000;	//0xFE760000 12位写0（设置输出低电平）  28位写1（写使能)	*virt_dr |= 0x10000000;	return 0;}
static int __init mycdev_init(void)
{
	major = register_chrdev(0, MY_NAME, &fops);
	if(major < 0)
	{
		printk("reg failed!\n");
		return -1;
	}
	printk("reg successed\n");
	my_led_init();    return 0;
}
int my_led_deinit(void){	//0xFE760000 12位写0（设置输出低电平）  28位写1（写使能)	*virt_dr |= 0x10000000;	iounmap(virt_iomux);	iounmap(virt_ddr);	iounmap(virt_dr);	return 0;}
static void __exit mycdev_exit(void)
{
	my_led_deinit();	printk("hello world %s\n","exit");
	unregister_chrdev(major, MY_NAME);
}

module_init(mycdev_init);

module_exit(mycdev_exit);

MODULE_LICENSE("GPL");MODULE_AUTHOR("LiSir LiSir@qq.com");
