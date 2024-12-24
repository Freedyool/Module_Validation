#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/io.h>#include <linux/uaccess.h>#include <linux/device.h>#include <linux/of.h>
#include <linux/gpio.h>#include <linux/of_gpio.h>#define CDEV_NAME "myled"#define LED_NODE_PATH "/myled"#define LED_NODE_PROPERTY "gpio"int major = -1;int gpionum = -1;struct class *cls = NULL;struct device *dev = NULL;struct device_node *led_node = NULL;char kbuf[128] = {0};int my_open(struct inode *inode, struct file *file){	return 0;}ssize_t my_read (struct file *file, char __user *ubuf, size_t size, loff_t *offset)
{	return size;}ssize_t my_write (struct file *file, const char __user *ubuf, size_t size, loff_t *offset)
{	size = size > sizeof(kbuf)  ? sizeof(kbuf) : size;	if(copy_from_user(kbuf, ubuf, size))	{		printk("copy data from user failed!\n");		return -EINVAL;	}	if(kbuf[0] == '1')	{		gpio_set_value(gpionum,1); //设置高电平	}	else	{		gpio_set_value(gpionum,0); //设置低电平	}	return size;}
int my_close (struct inode *inode, struct file *file)
{	return 0;}struct file_operations fops = {
	.open = my_open,
	.read = my_read,
	.write = my_write,
	.release = my_close
};int gpio_init(void){	//获取节点	led_node = of_find_node_by_path(LED_NODE_PATH);	if(led_node == NULL)	{		printk("find node %s failed!\n",LED_NODE_PATH );		return -ENODEV;	}	//获取gpio编号	gpionum = of_get_named_gpio(led_node, LED_NODE_PROPERTY, 0);	if(gpionum < 0)	{		printk("get property %s failed!\n",LED_NODE_PROPERTY );		return -EINVAL;	}	//申请GPIO	if(gpio_request(gpionum,NULL))	{		printk("request gpio failed!\n");		return -EINVAL;	}		//设置GPIO为输出	if(gpio_direction_output(gpionum, 0))	{		printk("set gpio direction failed!\n");		return -EINVAL;	}	return 0;}
static int __init mydev_init(void)
{
	//注册字符设备	major = register_chrdev(0,CDEV_NAME,&fops);	if(major < 0)	{		printk("register chardev failed! \n");		return -1;	}		//自动创建设备节点	//提交目录信息	cls = class_create(THIS_MODULE,CDEV_NAME);	if(IS_ERR(cls))	{		printk("auto create node failed! \n");		return PTR_ERR(cls);	}		//提交设备信息	dev = device_create(cls,NULL,MKDEV(major,0),NULL,"myled0");	{		if(IS_ERR(dev))		{			printk("device create failed! \n");			return PTR_ERR(dev);		}	}		gpio_init();    return 0;
}
void gpio_deinit(void){	gpio_set_value(gpionum,0);	gpio_free(gpionum);}
static void __exit mydev_exit(void)
{
	gpio_deinit();	device_destroy(cls, MKDEV(major,0));	class_destroy(cls);	unregister_chrdev(major,CDEV_NAME);
}

module_init(mydev_init);

module_exit(mydev_exit);

MODULE_LICENSE("GPL");