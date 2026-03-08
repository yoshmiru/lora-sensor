#![no_std]
#![no_main]

use panic_halt as _;
use atmega_hal::prelude::*;
use atmega_hal::clock::MHz8;
use atmega_hal::usart::Baudrate;

#[atmega_hal::entry]
fn main() -> ! {
    let dp = atmega_hal::Peripherals::take().unwrap();
    let pins = atmega_hal::pins!(dp);
    
    // E220 制御ピン
    let mut m0 = pins.pd2.into_output();
    let mut m1 = pins.pd3.into_output();
    m0.set_low();
    m1.set_low();

    // 受信確認用 LED (PB0)
    let mut led = pins.pb0.into_output();
    led.set_low();

    // UART (9600bps)
    let mut serial = atmega_hal::usart::Usart::new(
        dp.USART,
        pins.pd0,
        pins.pd1.into_output(),
        Baudrate::<MHz8>::new(9600),
    );

    loop {
        // シリアルから1バイト受信 (ブロッキング)
        let _byte = nb::block!(serial.read()).unwrap();
        led.toggle();
    }
}
