#include <linux/init.h>
#include <linux/module.h>

int led_level = 0;
module_param(led_level,int,0664);
MODULE_PARM_DESC(led_level,"type is int,level=0-1024");

int len = 0;
int arr[10] = {0};
module_param_array(arr,int,&len,0664);
MODULE_PARM_DESC(arr,"type is arraylist");

char c ='A';
module_param(c,byte,0664);
MODULE_PARM_DESC(c,"type is byte");

static int __init demo_init(void)
{
	int i = 0;
	printk("hello world %s\n","init");
	printk("led_level = %d\n",led_level);
	for(i = 0;i < len;i++)
	{
		printk("arr[%d] = %d \n",i,arr[i]);
	}
	printk("c = %c\n",c);
    return 0;
}

static void __exit demo_exit(void)
{
	printk("hello world %s\n","exit");
}

module_init(demo_init);

module_exit(demo_exit);

MODULE_LICENSE("GPL");