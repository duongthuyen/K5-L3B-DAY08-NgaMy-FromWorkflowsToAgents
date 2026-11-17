# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025 Datasets & Benchmarks, https://arxiv.org/abs/2503.13657. Loại bằng chứng: taxonomy dựng từ trace đã gán nhãn tay, kèm đo inter-annotator agreement |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent gom được vào 14 failure mode thuộc 3 nhóm: (1) đặc tả/thiết kế hệ thống, (2) lệch giữa các agent, (3) kiểm chứng và kết thúc task. Phần lớn lỗi đến từ thiết kế hệ thống, không chỉ do năng lực model |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Trace của một số framework MAS mã nguồn mở (ChatDev, MetaGPT, AG2, …) chạy LLM thật trên task lập trình/toán/hỏi đáp. Không phải task giao dịch tiền có host chặn ghi như LogiX; tỉ lệ giữa các nhóm lỗi không chuyển nguyên sang lab này |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Trial fail của swarm ở seed 55 thuộc nhóm (3) **lỗi kiểm chứng**: swarm tin số ngày trễ trong ticket mà không đối chiếu order row. Đổi swarm (D) → workflow (A, luôn quote từ order row) thì lỗi này về 0: pass rate tăng khoảng 1/70 ≈ 0.014, pass^5 tăng khoảng 1/14 ≈ 0.07, seed variance về 0. Lỗi chỉ xuất hiện ở claim có delay trong ticket khác order row (public: chỉ C-002, ticket 5 ngày, order 2 ngày) |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool manifest v1.1, seed `11,22,33,44,55`, `data/public_claims.jsonl` (14 claim), `config/pricing.yaml`, evaluator `lab8.metrics.trial_pass`, cùng host `durability.issue_refund`. Biến duy nhất được thay đổi: **nguồn số ngày trễ dùng để quote** (swarm: ticket ở seed % 5 = 0; workflow: luôn order row). Gán nhãn lỗi bằng cách đọc trace có event `model_override` |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: refund cho claim lẽ ra `denied` (trả tiền sai, host không chặn được vì approval hợp lệ). Đo bằng pass rate, pass^5, seed min-max, variance và lý do fail trong `reports/ablation_r2.json`; kiểm thêm cost/success để thấy cái giá của các lời gọi peer |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_r2.json` (chạy trong `src/`)
- Run id / file report: `src/reports/ablation_r2.json`; trial fail duy nhất `R-swarm-C-002-s55`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng** trên bộ public. Workflow: pass rate 1.000, pass^5 1.000, seed min-max 1.000–1.000, variance 0.000000, cost/success 28.80 VND. Swarm: pass rate 0.986 (69/70), pass^5 0.929 (13/14), seed min-max 0.929–1.000, variance 0.000816, cost/success 49.57 VND. Fail duy nhất là C-002 seed 55: `status resolved != denied`. Theo MAST đây là nhóm (3) kiểm chứng: không có bước đối chiếu output của peer với nguồn sự thật. Không phải lỗi giao việc, vì handoff đúng allowlist và investigator trả đúng order row. Bộ public chỉ có một claim lệch delay, nên cỡ mẫu nhỏ; chưa kết luận được về tần suất trên bộ hidden
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi của swarm ở đây được cài sẵn có tính tất định (`seed % 5 == 0`), không phải hành vi tự phát của LLM thật, nên ablation chỉ xác nhận cách phân loại lỗi chứ không đo được tần suất lỗi thật. Cost là VND mô phỏng từ `pricing.yaml`. Kết luận đảo lại nếu một model thật đọc ticket tốt hơn order row trong trường hợp order row sai, ví dụ dữ liệu vận đơn cập nhật trễ

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
