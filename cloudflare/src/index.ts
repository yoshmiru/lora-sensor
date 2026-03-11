export interface Env {
	// 将来的に D1 データベースなどを使う場合はここに定義を追加します
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		// POST リクエストのみを受け付ける
		if (request.method === "POST") {
			try {
				// ESP32 から送られてくる JSON データを解析
				const data = await request.json();
				
				// データのログ出力 (Cloudflare の管理画面でリアルタイムに確認可能)
				console.log("Received LoRa Data:", data);

				// 成功レスポンスを返す
				return new Response(JSON.stringify({ 
					status: "success", 
					received: data 
				}), {
					headers: { "Content-Type": "application/json" },
					status: 200
				});

			} catch (err) {
				return new Response("Invalid JSON", { status: 400 });
			}
		}

		// GET など他のメソッドには 405 を返す
		return new Response("Method Not Allowed", { status: 405 });
	},
};
