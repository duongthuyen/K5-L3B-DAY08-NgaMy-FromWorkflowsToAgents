# Báo cáo cá nhân — 2A202604079_HoangThiThanhNga

## 1. Thông tin thành viên

- Họ tên: Hoàng Thị Thanh Nga
- MSSV: 2A202604079
- Email:
- GitHub: `Ngahoang2005`

## 2. Phần việc phụ trách

TV3: Shape C `orchestrator` + handoff/trace.

- File sở hữu: `src/lab8/shapes/orchestrator.py`, `src/tests/test_team_orchestrator.py`.
- CP4: rà trace của cả ba shape nhóm viết để tìm secret/PII (chỉ đọc, không sửa file của TV1/TV2).
- Mục 3.3 của `report/team/group_report.md`.

## 3. Đóng góp cụ thể

- **`bc3d56b`** feat(orchestrator): shape C với handoff allowlist và trace sạch.
  - Orchestrator đọc claim row trong code; row này (có `parent_secret`, `raw_headers`, ticket) không vào handoff hay trace.
  - Handoff dựng bằng `make_handoff` với `facts={}` và bốn tool chỉ đọc: `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`.
  - Số tiền lấy từ `compute_compensation` trên order row trong DB. Delay ghi trong ticket bị bỏ qua (không có khối `REFERENCE_WEAKNESS` như swarm).
  - Chỉ orchestrator gọi `durability.issue_refund`, với quote đầy đủ; truyền `crash_at`, không bắt `InjectedCrash` (CP3).
  - Trace ghi trên mọi nhánh return.
- **Test riêng** `src/tests/test_team_orchestrator.py`:
  - `test_handoff_only_allowlisted_keys`: handoff trên mọi claim public chỉ có key trong `ALLOWED_FIELDS`, `facts` ⊆ `FACT_KEYS`, tool ⊆ `READONLY_TOOLS`.
  - `test_trace_has_no_canary_or_raw_claim`: mọi claim × seed 0, 1, 5; trace và `RunResult` không chứa `CANARY_SECRET_`, `parent_secret`, `raw_headers`, `ticket`; `run_id` khớp.
- **Quyết định kỹ thuật:**
  - `facts={}` thay vì đưa delay/phí vào handoff: investigator tự đọc order row qua tool có kiểm `principal_id`, nên orchestrator không cần chuyển dữ kiện nào và không có cơ hội rò field ngoài allowlist.
  - Trace chỉ ghi tóm tắt của investigator (`order_visible`, `order_reason`, `policy_count`, `prior_refund_count`) và số tiền quote, không ghi order view đầy đủ.
  - Truyền quote đầy đủ vào `issue_refund`: host mới là nơi biết các refund trước đó trên cùng đơn và trần theo đơn; nếu shape tự trừ thì host trừ thêm lần nữa, ra số sai.

## 4. Bằng chứng

- Commit: `bc3d56b` (shape + test), `882f761` và `57f3545` (`TEAM.md`).
- `python -m pytest -q -m student -k orchestrator`: 62 passed.
- `python -m pytest -q tests/test_team_orchestrator.py`: 56 passed.
- `python -m pytest -q tests/test_handoff_secret.py tests/test_trace_contract.py`: 9 passed.
- `python -m pytest -q` (cổng host): 132 passed, 1 skipped.
- CP4 rà trace: 3 shape × 14 claim × 5 seed (0, 1, 2, 3, 5) = 210 lần chạy, quét trace + `RunResult` tìm `CANARY_SECRET_`, `CANARY_INTERNAL_`, `Bearer`, SĐT, địa chỉ, tên hàng, ghi chú nội bộ và nguyên văn ticket: 0 lần trùng. Lúc rà, `single` vẫn là stub (70/70 lần trả `not_implemented`), cần rà lại khi TV2 xong.

## 5. Công cụ AI đã dùng

- **Claude Code** (trong VS Code): đọc đề và tài liệu host, viết bản đầu `orchestrator.py` và `test_team_orchestrator.py`, viết script rà trace cho CP4, soạn nháp báo cáo này và mục 3.3.
- **Cách tự kiểm tra:**
  - Chạy lại các lệnh pytest ở mục 4 và đối chiếu số pass.
  - Đọc code đối chiếu với `docs/contracts.md` và docstring đầu `orchestrator.py`: handoff qua `make_handoff`, không ghi claim row vào trace, không bắt `InjectedCrash`.
  - So với `swarm_reference.py` để chắc chắn không copy khối `REFERENCE_WEAKNESS`.
  - Số liệu trong báo cáo lấy từ output lệnh đã chạy, không do AI tự điền.

## 6. Tự đánh giá

(Thành viên tự viết.)
