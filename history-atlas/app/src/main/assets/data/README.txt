本目录存放历史图鉴的离线数据文件。

- china.json —— 中国史数据（scope = "china"）
- world.json —— 世界史数据（scope = "world"）

这两个文件由数据同事（china-data / world-data）依据 `data/SCHEMA.md` 契约生成，
最终由 lead 从仓库根目录的 `data/` 复制进来。

文件格式：UTF-8 无 BOM 的 JSON 对象，顶层字段为
{ "version": 1, "scope": "...", "periods": [...], "events": [...], "figures": [...] }

App 在运行时通过 HistoryRepository 从 assets 读取，
缺失或解析失败时返回空数据集而不是崩溃。
