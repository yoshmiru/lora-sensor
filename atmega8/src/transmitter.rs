#![no_std]
#![no_main]

use panic_halt as _;
use atmega_hal::prelude::*;
use atmega_hal::clock::MHz8;
use atmega_hal::usart::Baudrate;
use ufmt::uwriteln;

#[atmega_hal::entry]
fn main() -> ! {
    let dp = atmega_hal::Peripherals::take().unwrap();
    let pins = atmega_hal::pins!(dp);
    
    // E220 制御ピンの設定
    let mut m0 = pins.pd2.into_output();
    let mut m1 = pins.pd3.into_output();
    m0.set_low();
    m1.set_low();

    let aux = pins.pd4.into_floating_input();

    // UART (USART) の初期化
    // Baudrate 構造体を直接使用
    let mut serial = atmega_hal::usart::Usart::new(
        dp.USART,
        pins.pd0,
        pins.pd1.into_output(),
        Baudrate::<MHz8>::new(9600),
    );

    let mut delay = atmega_hal::delay::Delay::<MHz8>::new();

    loop {
        while aux.is_low() {}

        let _ = uwriteln!(&mut serial, "Hello World LoRa (E220)!");

        delay.delay_ms(5000u16);
    }
}
