/*
 * 立创开发板软硬件资料与相关扩展板软硬件资料官网全部开源
 * 开发板官网：www.lckfb.com
 * 技术支持常驻论坛，任何技术问题欢迎随时交流学习
 * 立创论坛：https://oshwhub.com/forum
 * 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
 * 不靠卖板赚钱，以培养中国工程师为己任
 * Change Logs:
 * Date           Author       Notes
 * 2024-06-14     LCKFB-LP    first version
 */
 
#include "bsp_i2c.h"
#include "stdio.h"

void I2C_GPIO_INIT(void)
{
	GPIO_InitTypeDef	GPIO_InitStruct; // GPIO初始化结构体
	
	RCC_I2C_ENABLE();					 // 使能GPIO时钟
	
	GPIO_InitStruct.Pins = GPIO_SCL|GPIO_SDA;		// GPIO引脚
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;		// 开漏输出
	GPIO_InitStruct.Speed = GPIO_SPEED_HIGH;		// 输出速度高
	GPIO_Init(PORT_I2C, &GPIO_InitStruct);	    // 初始化

	SDA(1); // 设置SDA高电平
	SCL(1); // 设置SCL高电平

	GPIO_InitTypeDef GPIO_InitStruct_DBG; // GPIO调试引脚初始化结构体
	GPIO_InitStruct_DBG.Pins = GPIO_DBG;				// GPIO调试引脚
	GPIO_InitStruct_DBG.Mode = GPIO_MODE_OUTPUT_PP;	// 推挽输出
	GPIO_Init(PORT_DBG, &GPIO_InitStruct_DBG);	// 初始化调试引脚

	DBG(1); // 设置调试引脚高电平
	DBG(0); // 设置调试引脚高电平
	DBG(1); // 设置调试引脚高电平
	DBG(0); // 设置调试引脚高电平
}

void I2C_GPIO_DEINIT(void)
{
    GPIO_DeInit(PORT_I2C, GPIO_SCL|GPIO_SDA); // 复位I2C引脚
}

/******************************************************************
 * 函 数 名 称：IIC_Start
 * 函 数 说 明：IIC起始信号
 * 函 数 形 参：无
 * 函 数 返 回：无
 * 作       者：LC
 * 备       注：无
******************************************************************/
void IIC_Start(void)
{
	SDA_OUT();
	DBG(1); // 设置调试引脚高电平
	DBG(0);
	DBG(1);
	DBG(0);
	SDA(1);
	SCL(1);
	delay_us(4);
	SDA(0);
	DBG(1); // 设置调试引脚高电平
	DBG(0);
	DBG(1);
	DBG(0);
	delay_us(4);
	SCL(0);
}

/******************************************************************
 * 函 数 名 称：IIC_Stop
 * 函 数 说 明：IIC停止信号
 * 函 数 形 参：无
 * 函 数 返 回：无
 * 作       者：LC
 * 备       注：无
******************************************************************/
void IIC_Stop(void)
{
	SDA_OUT();
	SCL(0);
	SDA(0);
	delay_us(4);  
	SCL(1);
	delay_us(4);
	SDA(1);
	delay_us(4);
}

/******************************************************************
 * 函 数 名 称：IIC_Send_Ack
 * 函 数 说 明：主机发送应答
 * 函 数 形 参：0应答  1非应答
 * 函 数 返 回：无
 * 作       者：LC
 * 备       注：无
******************************************************************/
void IIC_Send_Ack(uint8_t ack)
{
	SCL(0);
	SDA_OUT();
	if(!ack) SDA(0);
	else     SDA(1);
	delay_us(2);
	SCL(1);
	delay_us(2);
	SCL(0);
}

/******************************************************************
 * 函 数 名 称：IIC_Wait_Ack
 * 函 数 说 明：等待从机应答
 * 函 数 形 参：无
 * 函 数 返 回：1=无应答   0=有应答
 * 作       者：LC
 * 备       注：无
******************************************************************/
uint8_t IIC_Wait_Ack(void)
{
	uint16_t uc_err_time = 0;

	SDA_IN();
	SDA(1);
	delay_us(1);
	SCL(1);
	delay_us(1);
	while (SDA_GET() != 0)
	{
		uc_err_time++;
		if (uc_err_time > 250) // 超时判断
		{
			IIC_Stop();
			return 1; // 无应答
		}
	}
	SCL(0);

	return 0;
}
/******************************************************************
 * 函 数 名 称：IIC_Write
 * 函 数 说 明：IIC写一个字节
 * 函 数 形 参：dat写入的数据
 * 函 数 返 回：无
 * 作       者：LC
 * 备       注：无
******************************************************************/
void IIC_Write(uint8_t data)
{
	int i = 0;
	SDA_OUT();
	SCL(0);//拉低时钟开始数据传输

	for( i = 0; i < 8; i++ )
	{
		SDA( (data & 0x80) >> 7 );
		data<<=1;
		delay_us(2);
		SCL(1);
		delay_us(2); 
		SCL(0);
		delay_us(2);
	}
}

/******************************************************************
 * 函 数 名 称：IIC_Read
 * 函 数 说 明：IIC读1个字节
 * 函 数 形 参：无
 * 函 数 返 回：读出的1个字节数据
 * 作       者：LC
 * 备       注：无
******************************************************************/
uint8_t IIC_Read(void)
{
	unsigned char i,receive=0;
	SDA_IN();//SDA设置为输入
	for(i=0;i<8;i++ )
	{
		SCL(0);
		delay_us(2);
		SCL(1);
		receive<<=1;
		if( SDA_GET() != 0 )
		{        
			receive++;   
		}
		delay_us(1); 
	}
	return receive;
}
