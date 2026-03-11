#ifndef F_CPU
#define F_CPU 1000000UL
#endif

#include <avr/io.h>
#include <util/delay.h>
#include <stdio.h>

// --- I2C (TWI) Functions ---
void i2c_init(void) {
    TWBR = 32; 
    TWSR = (1 << TWPS0); 
}

void i2c_start(void) {
    TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);
    while (!(TWCR & (1 << TWINT)));
}

void i2c_stop(void) {
    TWCR = (1 << TWINT) | (1 << TWSTO) | (1 << TWEN);
}

void i2c_write(uint8_t data) {
    TWDR = data;
    TWCR = (1 << TWINT) | (1 << TWEN);
    while (!(TWCR & (1 << TWINT)));
}

uint8_t i2c_read_ack(void) {
    TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA);
    while (!(TWCR & (1 << TWINT)));
    return TWDR;
}

uint8_t i2c_read_nack(void) {
    TWCR = (1 << TWINT) | (1 << TWEN);
    while (!(TWCR & (1 << TWINT)));
    return TWDR;
}

// --- AHT25 Functions ---
void aht25_init(void) {
    _delay_ms(100);
    i2c_start();
    i2c_write(0x38 << 1); 
    i2c_write(0xBE);      
    i2c_write(0x08);
    i2c_write(0x00);
    i2c_stop();
    _delay_ms(10);
}

void aht25_read(float *temp, float *humi) {
    uint8_t data[6];
    i2c_start();
    i2c_write(0x38 << 1);
    i2c_write(0xAC); 
    i2c_write(0x33);
    i2c_write(0x00);
    i2c_stop();
    _delay_ms(80); 
    i2c_start();
    i2c_write((0x38 << 1) | 1);
    for(int i=0; i<5; i++) data[i] = i2c_read_ack();
    data[5] = i2c_read_nack();
    i2c_stop();
    uint32_t h_raw = ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | (data[3] >> 4);
    uint32_t t_raw = ((uint32_t)(data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | data[5];
    *humi = (float)h_raw * 100 / 1048576;
    *temp = (float)t_raw * 200 / 1048576 - 50;
}

// --- UART & ADC Functions ---
void uart_init(void) {
    UCSRA = (1 << U2X); 
    UBRRH = 0; UBRRL = 12; 
    UCSRC = (1 << URSEL) | (3 << UCSZ0);
    UCSRB = (1 << TXEN);
}

void uart_putstr(const char *s) {
    while (*s) {
        while (!(UCSRA & (1 << UDRE)));
        UDR = *s++;
    }
}

void adc_init(void) {
    ADMUX = (1 << REFS0);
    ADCSRA = (1 << ADEN) | (1 << ADPS1) | (1 << ADPS0);
}

uint16_t adc_read(uint8_t ch) {
    ADMUX = (ADMUX & 0xF0) | (ch & 0x07);
    ADCSRA |= (1 << ADSC);
    while (ADCSRA & (1 << ADSC));
    return ADC;
}

int main(void) {
    DDRB |= (1 << PB0); 
    DDRD |= (1 << PD2) | (1 << PD3); 
    PORTD &= ~((1 << PD2) | (1 << PD3)); 

    uart_init();
    adc_init();
    i2c_init();
    aht25_init();

    char buffer[64];
    float temp, humi;

    while (1) {
        PORTB |= (1 << PB0); 
        uint16_t moisture = adc_read(0);
        aht25_read(&temp, &humi);
        
        // Send data
        sprintf(buffer, "M:%u, T:%.1f, H:%.1f\r\n", moisture, (double)temp, (double)humi);
        uart_putstr(buffer);
        
        _delay_ms(200);
        PORTB &= ~(1 << PB0); 
        _delay_ms(5000);
    }
    return 0;
}
