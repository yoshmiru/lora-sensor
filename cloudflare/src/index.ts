export interface Env {
	DB: D1Database;
	LINE_CHANNEL_ACCESS_TOKEN: string;
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		const signature = request.headers.get("x-line-signature");
		const isLine = signature !== null;

		// --- A. LoRa 受信処理 (ESP32 からのデータ) ---
		if (request.method === "POST" && !isLine) {
			try {
				const payload = await request.json() as any;
				const rawMessage = payload.message;

				const parts = rawMessage.split(',');
				const moistureRaw = parseInt(parts[0].split(':')[1]);
				const temperature = parseFloat(parts[1].split(':')[1]);
				const humidity = parseFloat(parts[2].split(':')[1]);

				let moisturePercent = ((559 - moistureRaw) / (559 - 233)) * 100;
				moisturePercent = Math.max(0, Math.min(100, moisturePercent));

				await env.DB.prepare(
					"INSERT INTO sensor_data (moisture, temp, humi) VALUES (?, ?, ?)"
				).bind(moisturePercent.toFixed(1), temperature, humidity).run();

				return new Response("Logged", { status: 200 });
			} catch (err) {
				return new Response("LoRa Data Error", { status: 400 });
			}
		}

		// --- B. LINE Webhook 処理 ---
		if (request.method === "POST" && isLine) {
			try {
				const body = await request.json() as any;
				const event = body.events[0];

				if (!event || !event.replyToken) {
					return new Response("No reply token", { status: 200 });
				}

				let replyText = "";
				if (!env.LINE_CHANNEL_ACCESS_TOKEN) {
					replyText = "エラー: LINE_CHANNEL_ACCESS_TOKEN が未設定です。";
				} else {
					const latest = await env.DB.prepare(
						"SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT 1"
					).first() as any;

					if (latest) {
						replyText = `【現在のハウス状況】\n💧水分: ${latest.moisture}%\n🌡温度: ${latest.temp}℃\n☁湿度: ${latest.humi}%\n(計測: ${latest.created_at})`;
					} else {
						replyText = "データがありません。LoRa 送信機を確認してください。";
					}
				}

				const lineResponse = await fetch("https://api.line.me/v2/bot/message/reply", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"Authorization": `Bearer ${env.LINE_CHANNEL_ACCESS_TOKEN}`
					},
					body: JSON.stringify({
						replyToken: event.replyToken,
						messages: [{ type: "text", text: replyText }]
					})
				});

				if (!lineResponse.ok) {
					const errorDetail = await lineResponse.text();
					console.error("LINE API Response Error:", lineResponse.status, errorDetail);
				}

				return new Response("OK", { status: 200 });

			} catch (err: any) {
				console.error("Worker Catch Error:", err.message);
				return new Response("Error", { status: 500 });
			}
		}

		return new Response("Not Found", { status: 404 });
	},
};
