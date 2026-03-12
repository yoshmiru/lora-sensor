export interface Env {
	DB: D1Database;
	LINE_CHANNEL_ACCESS_TOKEN: string;
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		const signature = request.headers.get("x-line-signature");
		const isLine = signature !== null;

		// --- A. LoRa 受信処理 (ESP32 からのバッチデータ) ---
		if (request.method === "POST" && !isLine) {
			try {
				const batch = await request.json() as any[];

				// まとめて D1 に保存するための準備
				const statements = batch.map(entry => {
					const parts = entry.message.split(',');
					const moistureRaw = parseInt(parts[0].split(':')[1]);
					const temperature = parseFloat(parts[1].split(':')[1]);
					const humidity = parseFloat(parts[2].split(':')[1]);

					let moisturePercent = ((559 - moistureRaw) / (559 - 233)) * 100;
					moisturePercent = Math.max(0, Math.min(100, moisturePercent));

					return env.DB.prepare(
						"INSERT INTO sensor_data (moisture, temp, humi) VALUES (?, ?, ?)"
					).bind(moisturePercent.toFixed(1), temperature, humidity);
				});

				// 一括実行 (Batch execution)
				await env.DB.batch(statements);

				return new Response("Batch Logged", { status: 200 });
			} catch (err) {
				return new Response("Batch Error", { status: 400 });
			}
		}

		// --- B. LINE Webhook 処理 (変更なし) ---
		if (request.method === "POST" && isLine) {
			try {
				const body = await request.json() as any;
				const event = body.events[0];
				if (!event || !event.replyToken) return new Response("OK");

				let replyText = "";
				const latest = await env.DB.prepare(
					"SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT 1"
				).first() as any;

				if (latest) {
					replyText = `【現在のハウス状況】\n💧水分: ${latest.moisture}%\n🌡温度: ${latest.temp}℃\n☁湿度: ${latest.humi}%\n(計測: ${latest.created_at})`;
				} else {
					replyText = "データがありません。";
				}

				await fetch("https://api.line.me/v2/bot/message/reply", {
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
				return new Response("OK");
			} catch (err) {
				return new Response("Error", { status: 500 });
			}
		}

		return new Response("Not Found", { status: 404 });
	},
};
