# Team

## Thông tin nhóm

- Tên nhóm: NgaMy
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/duongthuyen/K5-L3B-DAY08-NgaMy-FromWorkflowsToAgents, nhánh `main`, commit chốt: `d2eafae` (trùng `report/team/decision_adr.md`)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Dương Thị Huyền | 2A202604077 |       | `duongthuyen` | TV1: Shape A `workflow` (`src/lab8/shapes/workflow.py`) |
|   2 | Bùi Thu Phương | 2A202604080 |       | `buiphuong33` | TV2: Shape B `single` (`src/lab8/shapes/single.py`) |
|   3 | Hoàng Thị Thanh Nga | 2A202604079 |       | `Ngahoang2005` | TV3: Shape C `orchestrator` + handoff/trace (`src/lab8/shapes/orchestrator.py`) |
|   4 | Phạm Minh Tâm |      |       | `minhtama11qc-hash` | TV4: Evaluation, crash suite, ADR, research card, báo cáo|

Phân công chi tiết, file sở hữu và lịch theo checkpoint: [report/team/group_report.md](report/team/group_report.md) mục 2.

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Dương Thị Huyền (`duongthuyen`) | Shape A `workflow` | `c59cf58` feat(workflow): cài shape A workflow | `src/tests/test_team_workflow.py` |
| Bùi Thu Phương (`buiphuong33`) | Shape B `single` | `281de5a` feat(single): implement shape B ReAct agent with team tests | `src/tests/test_team_single.py` |
| Hoàng Thị Thanh Nga (`Ngahoang2005`) | Shape C `orchestrator` + handoff/trace | `bc3d56b` feat(orchestrator): shape C với handoff allowlist và trace sạch | `src/tests/test_team_orchestrator.py` |
| Phạm Minh Tâm (`minhtama11qc-hash`; phần đầu do Dương Thị Huyền làm thay) | Evaluation + báo cáo | Huyền làm thay: `5814f68` chore(eval): crash suite, ablation R2, research card; `d2eafae` benchmark 4 shape. Tâm: `dcfdbb2` test(eval): crash/resume cho single và orchestrator, kiểm hidden_selfcheck | `src/tests/test_team_reports.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
