# Báo cáo cá nhân — 2A202604080_BuiThuPhuong

## 1. Thông tin thành viên

- Họ tên: Bùi Thu Phương
- MSSV: 2A202604080
- Email: buithuphuongg1303@gmail.com
- GitHub: buiphuong33

## 2. Phần việc phụ trách

TV2: **Shape B `single`**, một agent ReAct duy nhất.

| Phần                      | File                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------ |
| Code shape                | `src/lab8/shapes/single.py`                                                          |
| Test của nhóm cho shape B | `src/tests/test_team_single.py`                                                      |
| Checkpoint                | CP2 (cài shape), CP3 (crash/idempotency), CP4 (crash, approval, secret) trên shape B |

## 3. Đóng góp cụ thể

**Commit chính:** `281de5a` feat(single): implement shape B ReAct agent with team tests (nhánh `feat/shape-b-single`).

**Cách shape B chạy:**

1. Vòng ReAct qua `lab8.runtime.run_react`, tối đa **8 bước** (`MAX_STEPS = 8`). Mỗi bước, `decide()` chọn một tool **chỉ đọc** theo thứ tự `get_claim_view` → `lookup_order` → `lookup_refund_history` → `compute_compensation`, rồi trả `final`.
2. Dừng sớm khi: không thấy claim → `failed`; thiếu `order_id` → `needs_info`; order không thuộc khách → `escalated`. Không ghi ledger ở các nhánh này.
3. Sau vòng lặp, **code** (không phải agent) gọi `durability.issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=crash_at)`. Quote bằng 0 → `denied`, không gọi host.

**Quyết định kỹ thuật:**

- **Scratchpad riêng cho agent.** `run_react` chỉ đưa cho `decide` kết quả của tool vừa gọi, nên agent giữ dict `memory` qua các bước. Nếu không, bước sau mất `order_id` và quote của bước trước.
- **Ranh giới code / model.** Số tiền lấy từ kết quả tool `compute_compensation` lưu trong `memory`, không lấy từ câu trả lời `final` của model. Agent không có tool ghi; `runtime.dispatch` chặn `issue_refund` bằng `ToolRejected`.
- **Truyền quote đầy đủ** cho host, không tự trừ phần đã hoàn. Host tự trừ theo trần của đơn; nếu shape trừ trước thì bị trừ hai lần và T14 fail.
- **Ticket là dữ liệu.** Prompt của mỗi bước chỉ có số bước và tên tool vừa gọi, không có ticket. Số ngày trễ lấy từ order row, nên câu như "IGNORE POLICY" hay "trễ 30 ngày" không đổi kết quả.
- **Trace cố ý không ghi:** claim row, `principal_id`, ticket, `parent_secret`, `raw_headers`, phone, address, câu trả lời soạn cho khách. Trace chỉ ghi tên tool, order view đã allowlist, quote, kết quả host và quyết định cuối.
- **Crash (CP3).** Truyền `crash_at` vào `issue_refund`. `InjectedCrash` không bị nuốt: shape ghi trace rồi `raise` lại để lần chạy sau resume.
- **Chi phí đếm được.** Mỗi bước ReAct là một lần gọi MockLLM (`purpose="react"`), cộng một lần soạn câu trả lời. Claim resolved tốn 6 lần gọi model, workflow chỉ tốn 1. Con số này dùng để so sánh trong ADR.

**Test đã thêm:** `src/tests/test_team_single.py`, 63 test:

| Nhóm test                                                                       | Kiểm gì                                                                                    |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `test_ticket_text_cannot_change_amount`, `test_ticket_text_never_reaches_trace` | Ticket bị chèn lệnh vẫn ra 35.000, chữ trong ticket không vào trace                        |
| `test_write_tool_from_decide_is_rejected`                                       | Agent tự gọi `issue_refund` thì bị `ToolRejected`, ledger trống                            |
| `test_step_cap_fails_closed`                                                    | Agent lặp mãi thì dừng ở bước 8, `failed` / `step_cap`, không hoàn tiền                    |
| `test_resolved_claim_uses_counted_model_calls`, `test_needs_info_stops_early`   | Đếm đúng số lần gọi model và tool                                                          |
| `test_full_quote_passed_to_host`                                                | T14: shape truyền 150.000, ledger ghi 120.000                                              |
| `test_repeat_call_keeps_one_ledger_row`                                         | Chạy lại cùng claim, chỉ một refund                                                        |
| `test_crash_then_resume_pays_once`                                              | 7 claim có hoàn tiền × 3 điểm crash, resume xong đúng 1 refund, 1 audit                    |
| `test_broken_approval_never_pays_even_on_retry`                                 | Thiếu approval, approval của claim khác, bị thu hồi, hết hạn: `denied`, kể cả khi chạy lại |
| `test_stale_approval_and_refunded_order_denied`                                 | C-007, C-013 `denied`, không ghi ledger                                                    |
| `test_trace_has_no_secret_or_raw_fields`                                        | 14 claim × 2 seed, quét trace + kết quả + stdout                                           |

## 4. Bằng chứng

Chạy trong `src/`, commit `281de5a`:

| Lệnh                                                                                                         | Kết quả                                                               |
| ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| `python -m pytest -q -m student -o addopts= -k "single and not orchestrator and not workflow and not swarm"` | 62 passed (ma trận public T01–T14 của shape single, gồm T11, T12)     |
| `python -m pytest -q tests/test_team_single.py`                                                              | 63 passed                                                             |
| `python -m pytest -q` (cổng host)                                                                            | 139 passed, 1 skipped                                                 |
| `python -m lab8.crash_test --count 20 --out <thư mục tạm>`                                                   | `crash_safety 20/20` (không ghi đè `src/reports/crash.json` của nhóm) |

Ghi chú: lệnh tự kiểm trong `CHECKPOINTS.md` là `-k single`, nhưng `-k single` khớp cả tên hàm `test_public_single_run_cases` nên chạy test của mọi shape. Phải lọc thêm như lệnh trên mới ra đúng 62 test của shape single.

Số liệu benchmark và run id của shape B nằm trong `src/reports/benchmark.json` sau khi nhóm chạy CP5.

## 5. Công cụ AI đã dùng

**Công cụ:** Claude Code (Claude Opus 5.5) trong VS Code.

**Dùng vào việc gì:**

- Giải thích đề bài và các khái niệm: ReAct, MockLLM, ticket, canary, host, idempotency.
- Đọc code có sẵn (`runtime.py`, `tools.py`, `workflow.py`, `swarm_reference.py`) và **sinh code** `single.py`.
- **Sinh file test** `test_team_single.py` và một script tự kiểm CP4 tạm thời (crash × approval × quét secret).

**Tự kiểm tra kết quả:**

- Đọc lại `single.py` để tự giải thích được: vì sao cần scratchpad, vì sao số tiền lấy từ tool chứ không từ model, vì sao truyền quote đầy đủ, trace không ghi field nào.
- Xem file trace trong `src/traces/` của shape single, kiểm tra không có `CANARY_SECRET_`, ticket hay `principal_id`.
- Xác nhận không sửa file thước đo (`metrics.py`, `durability.py`, `policy.py`, `config/`, `data/`) và không sửa tay JSON trong `src/reports/`.

## 6. Tự đánh giá

...
