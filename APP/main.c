/*
 * ������������Ӳ�������������չ����Ӳ�����Ϲ���ȫ����Դ
 * �����������www.lckfb.com
 * ����֧�ֳ�פ��̳���κμ������⻶ӭ��ʱ����ѧϰ
 * ������̳��https://oshwhub.com/forum
 * ��עbilibili�˺ţ������������塿���������ǵ����¶�̬��
 * ��������׬Ǯ���������й�����ʦΪ����
 * Change Logs:
 * Date           Author       Notes
 * 2024-06-12     LCKFB-LP    first version
 */
#include "board.h"
#include "stdio.h"
#include "bsp_uart.h"
#include "bsp_i2c.h"
#include "driver_ina226_interface.h"
#include "driver_ina226_basic.h"

int32_t ina226_poll(uint32_t times);

int32_t main(void)
{
	board_init();	// �������ʼ��
	
	uart1_init(115200);	// ����1������115200
	
	GPIO_InitTypeDef	GPIO_InitStruct; // GPIO��ʼ���ṹ��
	
	__RCC_GPIOC_CLK_ENABLE();	// ʹ��GPIOʱ��
	
    GPIO_InitStruct.Pins = GPIO_PIN_13;				// GPIO����
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;		// �������
    GPIO_InitStruct.Speed = GPIO_SPEED_HIGH;		// ����ٶȸ�
    GPIO_Init(CW_GPIOC, &GPIO_InitStruct);			// ��ʼ��
	
	I2C_GPIO_INIT();

	for (int32_t i = 0; i < 16; i++)
	{
		IIC_Start();
		IIC_Stop();
		delay_ms(1000);
	}

	// ina226_basic_init(INA226_ADDRESS_0, 0.1); // ��ʼ��INA226����ַΪ0x40���ֱ���Ϊ0.1mV

    delay_ms(20);

	while(1)
	{
		// �ߵ�ƽ
		GPIO_WritePin(CW_GPIOC, GPIO_PIN_13, GPIO_Pin_SET);
		// printf("[SET]\r\n");
		delay_ms(100);

		// ��ѯINA226����ȡ10������
		// printf("ina226 poll %x\r\n", ina226_poll(10));;

		// �͵�ƽ
		GPIO_WritePin(CW_GPIOC, GPIO_PIN_13, GPIO_Pin_RESET);
		// printf("[RESET]\r\n");
		delay_ms(100);
	}
}

int32_t ina226_poll(uint32_t times)
{
	uint32_t i;
	uint8_t res;

	for (i = 0; i < times; i++)
	{
		float mV;
		float mA;
		float mW;

		res = ina226_basic_read(&mV, &mA, &mW);
		if (res != 0)
		{
			(void)ina226_basic_deinit();

			return 1;
		}

		ina226_interface_debug_print("ina226: %d/%d.\r\n", i + 1, times);
		ina226_interface_debug_print("ina226: bus voltage is %0.3fmV.\r\n", mV);
		ina226_interface_debug_print("ina226: current is %0.3fmA.\r\n", mA);
		ina226_interface_debug_print("ina226: power is %0.3fmW.\r\n", mW);
		ina226_interface_delay_ms(1000);
	}

	return 0;
}