# Báo cáo cá nhân — 2A202604097_PhamMinhTam

## 1. Thông tin thành viên

- Họ tên: Phạm Minh Tâm
- MSSV: 2A202604097
- Email: minhtama11qc@gmail.com
- GitHub: `minhtama11qc-hash`

## 2. Phần việc phụ trách

- **TV4: Evaluation, durability, báo cáo.**
- Mình vào repo nhóm muộn. Phần TV4 đã có trước đó (crash suite, benchmark 4 shape, ablation R2, research card, ADR, tự kiểm hidden, `check_submission`) do Dương Thị Huyền làm thay. Các commit `5814f68`, `d2eafae`, `6414cb0`, `fcc01a4` là của Huyền, ghi trong `TEAM.md` và báo cáo cá nhân của Huyền.
- Sau khi vào repo, mình làm phần bổ sung cho TV4, không làm lại phần đã có:
  - File sở hữu: `src/tests/test_team_reports.py` (phần thêm ở cuối file).
  - Cập nhật dòng TV4 trong `TEAM.md` và mục 6 của `report/team/group_report.md`.

## 3. Đóng góp cụ thể

- **`d8ca1c0`** docs(team): điền GitHub `minhtama11qc-hash` của TV4 vào `TEAM.md` và `group_report.md`, bỏ ghi chú "chưa vào repo". Các commit TV4 cũ vẫn ghi là Huyền làm thay.
- **`dcfdbb2`** test(eval): mở rộng `src/tests/test_team_reports.py` từ 6 lên 15 test.
  - **Must-pass 3 trên `single` và `orchestrator`:** trước đó file chỉ test crash/resume trên `workflow`. Mình thêm test cho 2 shape còn lại, ở cả 3 điểm crash (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`). Sau khi resume, claim C-012 vẫn `resolved`, refund đúng 35.000 VND và chỉ có 1 audit `refund_committed`.
  - **Chạy lại không crash:** chạy cùng một claim hai lần trên cả 3 shape vẫn chỉ ra 1 audit `refund_committed`, tức là không trả tiền hai lần.
  - **Kiểm `hidden_selfcheck.json`:** group report và ADR có trích dẫn file này. Test kiểm seed đúng `11,22,33,44,55`; 3 shape nhóm viết có 0 `error_trials` và 0 `leak_suspect_trials`; 3 shape cùng status ở mọi cặp (claim, seed). Như vậy nếu ai chạy lại tự kiểm mà kết quả lệch với báo cáo thì test sẽ đỏ.
  - Lý do chọn phần này: rubric yêu cầu crash an toàn (must-pass 3) cho shape được chọn, nhưng nếu nhóm đổi sang `single` hoặc `orchestrator` thì trước đây chưa có test nào giữ điều này.

## 4. Bằng chứng

Chạy trong `src/`:

```text
$ python -m pytest -q tests/test_team_reports.py
15 passed

$ python -m pytest -q
206 passed, 248 deselected

$ python -m lab8.check_submission
0 FAIL, 0 WARN
```

- Commit: `d8ca1c0` (cập nhật thông tin), `dcfdbb2` (test).

## 5. Công cụ AI đã dùng

- Dùng Claude Code để đọc repo, tìm phần TV4 còn thiếu theo `RUBRIC.md` (C8: mỗi người cần commit có nội dung và test), viết test và soạn báo cáo này.
- Mình kiểm lại bằng cách chạy toàn bộ test và `check_submission` trước khi commit.

## 6. Tự đánh giá

- Phần đóng góp của mình nhỏ hơn các thành viên khác vì vào nhóm muộn; phần chính của TV4 là Huyền làm.
- Phần bổ sung giúp must-pass 3 được kiểm trên cả 3 shape nhóm viết, và số liệu tự kiểm hidden trong báo cáo có test giữ.
