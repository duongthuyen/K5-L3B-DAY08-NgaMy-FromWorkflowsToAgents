# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: NgaMy
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `d2eafae`

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

### 2.1 Phân công (4 người)

Nguyên tắc chia: **mỗi người sở hữu riêng một nhóm file**, không ai sửa file của người khác, nên 4 người làm song song từ CP2 mà không đụng merge. Ba shape A/B/C độc lập với nhau (chỉ dùng chung host có sẵn, không ai được sửa host). Mỗi người có ít nhất một commit có nội dung và **một file test riêng** để đáp ứng C8.

> Thành viên lấy theo collaborators của repo nhóm: Dương Thị Huyền (`duongthuyen`, chủ repo), `buiphuong33` (Bùi Thu Phương), `Ngahoang2005`. Thành viên thứ tư **Phạm Minh Tâm** chưa vào repo; phần TV4 do Dương Thị Huyền làm thay, trong `TEAM.md` và báo cáo cá nhân ghi đúng như vậy. Vì Huyền gánh hai phần nên nhận shape đơn giản nhất (workflow). MSSV điền khi chốt `TEAM.md`.

| Người | Vai | File sở hữu (chỉ người này sửa) | Test riêng | Hạng mục rubric chịu trách nhiệm |
| --- | --- | --- | --- | --- |
| TV1 — Dương Thị Huyền (`duongthuyen`) | Shape A `workflow` | `src/lab8/shapes/workflow.py` | `src/tests/test_team_workflow.py` | C1 (A), C3 + C4 trên A |
| TV2 — Bùi Thu Phương (`buiphuong33`) | Shape B `single` (ReAct) | `src/lab8/shapes/single.py` | `src/tests/test_team_single.py` | C1 (B), C3 + C4 trên B |
| TV3 — `Ngahoang2005` | Shape C `orchestrator` + handoff/trace | `src/lab8/shapes/orchestrator.py` | `src/tests/test_team_orchestrator.py` | C1 (C), C5 |
| TV4 — Phạm Minh Tâm (làm thay: Dương Thị Huyền) | Evaluation, durability check, báo cáo | `src/reports/*.json` (chỉ sinh bằng lệnh), `report/team/decision_adr.md`, `report/team/research_card.md`, `report/team/group_report.md` (mục 1, 4, 7, 8), `TEAM.md` (phần thông tin nhóm) | `src/tests/test_team_reports.py` | C2, C6, C7, must-pass trên shape chọn |

File dùng chung, mỗi người **chỉ sửa phần của mình**: dòng của mình trong bảng đóng góp `TEAM.md`; mục 3 (đoạn về shape mình) và mục 5 của `group_report.md`; báo cáo cá nhân `report/team/MSSV_HoTen.md` (mỗi người một file riêng, copy từ mẫu).

**Không ai được sửa:** `src/lab8/metrics.py`, `durability.py`, `policy.py`, `src/config/*`, `src/data/*`, `src/lab8/shapes/swarm_reference.py`, `src/lab8/shapes/__init__.py`, và không sửa tay JSON trong `src/reports/`.

### 2.2 Việc cụ thể từng người

**TV1 — Dương Thị Huyền: Shape A `workflow`**

- CP2: làm 8 bước trong docstring `workflow.py`: đọc claim qua `get_claim_view`; thiếu `order_id` thì trả `needs_info`; không thấy order thì `escalated`; quote bằng `compute_compensation` từ order row (bỏ qua số delay trong ticket); quote 0 thì `denied`; quote > 0 thì `durability.issue_refund` với **quote đầy đủ**; trả qua `common.finish()`; ghi trace ở mọi nhánh return.
- CP3: truyền `crash_at` vào `issue_refund`, không bắt `InjectedCrash`. Không copy khối `REFERENCE_WEAKNESS` của swarm.
- Tự kiểm: `python -m pytest -q -m student -o addopts= -k workflow` → 62 passed.
- Test riêng: một claim gọi 2 lần vẫn 1 dòng ledger; ticket ghi "ignore policy"/delay giả không đổi số tiền.

**TV2 — Bùi Thu Phương: Shape B `single`**

- CP2: dùng `lab8.runtime.run_react` với `max_steps=8`; `decide` chỉ chọn tool đọc (`lookup_order`, `lookup_refund_history`…) và không bao giờ gọi `issue_refund`. Sau vòng lặp, code tính quote từ order row rồi gọi `durability.issue_refund` với quote đầy đủ. Đếm model call vào `Budget`.
- CP3: truyền `crash_at`, không bắt `InjectedCrash`.
- Tự kiểm: `-k single` → 62 passed.
- Test riêng: vòng lặp dừng ≤ 8 bước; ticket khai delay cao hơn order row thì vẫn quote theo order row; đơn đã hoàn một phần thì host cắt đúng trần (T13/T14).

**TV3 — `Ngahoang2005`: Shape C `orchestrator` + handoff/trace**

- CP2: dựng handoff bằng `lab8.handoff.make_handoff`, chỉ field allowlist và tool chỉ đọc; chạy `run_readonly_investigators`; orchestrator quote từ order view và gọi `issue_refund`.
- CP3: trace chỉ ghi handoff đã sanitize, không ghi parent context, `parent_secret`, header, SĐT, địa chỉ, ghi chú nội bộ, tên hàng. Truyền `crash_at`.
- CP4: rà trace của **cả ba shape** để tìm `CANARY_SECRET_*`/PII (chỉ đọc trace và báo cho TV1/TV2, không sửa file của họ).
- Tự kiểm: `-k orchestrator` → 62 passed; `python -m pytest -q tests/test_handoff_secret.py tests/test_trace_contract.py`.
- Test riêng: handoff không chứa key ngoài allowlist; trace của orchestrator không chứa chuỗi `CANARY_SECRET_`.

**TV4 — Phạm Minh Tâm (Dương Thị Huyền làm thay): Evaluation, durability, báo cáo**

- CP1: tạo repo nhóm đúng tên `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` và mời giảng viên vào repo; điền phần thông tin nhóm trong `TEAM.md`; chọn câu R1–R4 và điền SOURCE/CLAIM/BOUNDARY trong `research_card.md` (không cần đợi code).
- CP2–CP3 (song song với các shape): chạy benchmark/crash trên `swarm` để dựng sẵn quy trình; viết `test_team_reports.py` (ví dụ: kiểm `reports/benchmark.json` có đủ 4 shape và seed `11,22,33,44,55`, `crash.json` có `crash_safety` = `20/20`).
- CP4: chạy `python -m lab8.crash_test --count 20 --out reports/crash.json` → `20/20`.
- CP5: sau khi merge 3 shape, chạy `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`; tự kiểm trên `student_drop/`; cả nhóm chọn shape dựa trên số đo, TV4 điền `decision_adr.md` (shape chọn, commit hash, run id, số lấy từ file report); chạy ablation cho research card; viết mục 1, 4, 7, 8 của báo cáo này; chạy `python -m lab8.check_submission` → `0 FAIL` rồi push.

### 2.3 Lịch làm song song và quy trình git

| Mốc | TV1 Huyền | TV2 Phương | TV3 `Ngahoang2005` | TV4 Tâm (Huyền làm thay) |
| --- | --- | --- | --- | --- |
| CP1 (13:30) | cài môi trường, smoke pass, đọc `business_rules.md`, `contracts.md`, `swarm_reference.py` (cả nhóm) | ← | ← | + tạo repo, `TEAM.md`, research card |
| CP2 (13:45) | workflow | single | orchestrator | benchmark/crash thử trên swarm, test report |
| CP3 (14:30) | `crash_at`, T11/T12 | `crash_at`, T11/T12 | handoff sanitize, trace | — |
| CP4 (15:30) | sửa lỗi T01–T14 | sửa lỗi T01–T14 | rà secret/PII trên cả 3 trace | crash suite 20/20 |
| CP5 (16:15) | báo cáo cá nhân, mục 3 (A) | báo cáo cá nhân, mục 3 (B) | báo cáo cá nhân, mục 3 (C) | benchmark, ADR, research card, check_submission |

- Mỗi người làm trên nhánh riêng: `feat/workflow`, `feat/single`, `feat/orchestrator`, `chore/eval-report`. Merge vào `main` qua PR; vì không ai sửa chung file nên không có conflict code.
- Trước mỗi lần push: `python -m pytest -q` (cổng host) phải xanh.
- Thứ tự merge: mỗi shape merge ngay khi đạt 62 passed; TV4 chỉ chạy benchmark chính thức và ghi commit hash **sau khi đã merge đủ 3 shape**, để số liệu khớp commit chốt (C7).
- Không force-push, không commit `traces/`, `*.sqlite`, `student_drop/`, `.venv/`, `.env`.

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### 3.1 Shape A `workflow` (TV1 — Dương Thị Huyền)

- **Đọc:** `get_claim_view` (không `SELECT *`), rồi `lookup_order` theo `principal_id` của claim (chỉ trả field allowlist: `order_id`, `status`, `delay_days`, `shipping_fee_vnd`, `paid_vnd`, `damage_verified`, `carrier`).
- **Quyết định (toàn bộ bằng code):** thiếu `order_id` → `needs_info`; order không thấy hoặc ngoài phạm vi khách → `escalated`; quote bằng `compute_compensation` từ order row và policy hiện hành; quote 0 → `denied` (không gọi host, nên không có audit `policy_denied`); quote > 0 → `durability.issue_refund(conn, claim_id, quote đầy đủ, crash_at=crash_at)`. Host từ chối → `denied`; xung đột số tiền → `failed`; thành công → `resolved`.
- **Ranh giới code / model:** ticket không bao giờ được parse lấy số; MockLLM chỉ được gọi **một lần** để soạn câu trả lời, sau khi số tiền đã chốt. Câu "ignore policy" trong ticket không có tác dụng (test `test_ticket_text_cannot_change_amount`).
- **Crash:** `InjectedCrash` không bị bắt lại; trace được ghi ra rồi ném tiếp để chạy lại (resume) vẫn chỉ ra một refund.
- **Trace:** event `claim` (claim_id, `has_order_id`), `lookup_order` (order view đã allowlist hoặc lý do không thấy), `quote`, `issue_refund` (ok/conflict/reason), `crash`, `decision`. Cố ý **không** ghi: claim row, `principal_id`, ticket, `parent_secret`, header, câu trả lời của model.
- **Kết quả hiện có:** 62/62 test student (`-k workflow`); trên bộ public 14 claim × 5 seed: pass rate 1.000, pass^5 1.000, variance 0, cost/success 28.80 VND (`src/reports/ablation_r2.json`).

### 3.2 Shape B `single` (TV2)

...

### 3.3 Shape C `orchestrator` (TV3)

- **Đọc:** orchestrator đọc claim row (`principal_id`, `order_id`, ticket) trong code để định tuyến; row này **không** vào handoff hay trace. Investigator nhận handoff và chạy qua `run_readonly_investigators` với bốn tool chỉ đọc: `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`.
- **Handoff:** dựng bằng `make_handoff` với `facts={}`, `task="check_applicable_policy"`. Allowlist nằm trong code (`ALLOWED_FIELDS`, `FACT_KEYS`, `READONLY_TOOLS`), `sanitize` chặn canary và tool ghi. Không dùng LLM để tóm tắt context thay cho allowlist.
- **Quyết định (toàn bộ bằng code):** không có claim → `failed`; thiếu `order_id` → `needs_info`; order không thấy hoặc ngoài phạm vi khách → `escalated`; quote từ `compute_compensation` trên order row; quote 0 → `denied`; quote > 0 → orchestrator gọi `durability.issue_refund(conn, claim_id, quote đầy đủ, crash_at=crash_at)`. Host từ chối → `denied`; xung đột → `failed`; thành công → `resolved`.
- **Ranh giới code / model:** MockLLM chỉ được gọi để đọc ticket (`parse`) và soạn câu trả lời (`draft`); không số nào từ model dùng để tính tiền. Delay ghi trong ticket bị bỏ qua, khác swarm (không có `REFERENCE_WEAKNESS`). Investigator không có tool ghi.
- **Crash:** `InjectedCrash` không bị bắt lại; trace được ghi rồi ném tiếp để chạy lại vẫn chỉ ra một refund.
- **Trace:** event `handoff` (đã sanitize), `investigator` (`claim_view` allowlist, `order_visible`, `order_reason`, `policy_count`, `prior_refund_count`), `quote` (`amount_vnd`, `reason`), `crash`, `decision`. Cố ý **không** ghi: claim row, `principal_id`, ticket, `parent_secret`, header, order view đầy đủ, câu trả lời của model.
- **Kết quả hiện có:** 62/62 test student (`-k orchestrator`); test riêng `test_team_orchestrator.py` 56 passed.
- **CP4 (rà trace cả ba shape):** 3 shape × 14 claim × 5 seed = 210 lần chạy, quét trace + `RunResult` tìm canary, `Bearer`, SĐT, địa chỉ, tên hàng, ghi chú nội bộ, nguyên văn ticket: 0 lần trùng. Lúc rà, `single` còn là stub, cần rà lại sau khi TV2 xong.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

Lệnh (chạy trong `src/`): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`. 14 claim × 5 seed = 70 trial mỗi shape, MockLLM, mỗi trial một SQLite mới.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps | Model calls TB |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A `workflow` | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.80 | 4.43 / 5 | 1.00 |
| B `single` | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 39.44 | 6.29 / 7 | 5.64 |
| C `orchestrator` | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 57.14 | 3.71 / 4 | 2.00 |
| D `swarm` | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 |

- Swarm fail đúng 1 trial: `R-swarm-C-002-s55` (`status resolved != denied`). Ở seed 55, swarm tin số ngày trễ khách ghi trong ticket (5 ngày) thay vì order row (2 ngày) nên hoàn tiền cho claim lẽ ra phải từ chối.
- Không trial nào có `leak_suspect`. T07 (approval hỏng) và T13 (approval sai claim) pass ở cả 4 shape và 5 seed.
- Crash safety: `20/20` (`python -m lab8.crash_test --count 20 --out reports/crash.json`).
- Ma trận student: 248/248 (4 shape × 62). Cổng host `python -m pytest -q`: xanh.
- `student_drop/` chưa có tại thời điểm chạy nên chưa tự kiểm trên bộ hidden.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

**TV3 (`Ngahoang2005`)**

- Script rà trace chạy ngoài `src/` báo `ModuleNotFoundError: No module named 'lab8'`. Xử lý: đặt `PYTHONPATH` trỏ tới `src/` trước khi chạy (Windows PowerShell: `$env:PYTHONPATH = (Get-Location).Path`).
- Máy chưa cài GitHub CLI (`gh: command not found`) nên không tạo PR bằng dòng lệnh; push nhánh `feat/orchestrator` rồi đưa lên `main` bằng fast-forward (chỉ có commit của TV3, không đụng file người khác).

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

- **Dương Thị Huyền (TV1, 2A202604077)**:
  - Phần việc: shape A `workflow` (`c59cf58`), đạt 62/62 test student; test riêng `test_team_workflow.py`.
  - Điều phối: chia việc, điền `TEAM.md`, kiểm tra và merge nhánh. Báo cáo: `report/team/2A202604077_DuongThiHuyen.md`.
- **Phạm Minh Tâm (TV4, phần việc do Dương Thị Huyền làm thay)**:
  - Đã xong (`5814f68`): crash suite 20/20 (`src/reports/crash.json`); ablation R2 (`src/reports/ablation_r2.json`); research card; test riêng `test_team_reports.py`.
  - Còn lại ở CP5: benchmark 4 shape, ADR, `check_submission`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
