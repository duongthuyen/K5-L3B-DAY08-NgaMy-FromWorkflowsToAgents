# Team

## Thông tin nhóm

- Tên nhóm: NgaMy
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/duongthuyen/K5-L3B-DAY08-NgaMy-FromWorkflowsToAgents, nhánh `main`, commit chốt: (điền ở CP5, trùng `report/team/decision_adr.md`)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | (điền họ tên) |      |       | `duongthuyen` | TV1: Shape A `workflow` (`src/lab8/shapes/workflow.py`) |
|   2 | Bùi Thu Phương |      |       | `buiphuong33` | TV2: Shape B `single` (`src/lab8/shapes/single.py`) |
|   3 | (điền họ tên) |      |       | `Ngahoang2005` | TV3: Shape C `orchestrator` + handoff/trace (`src/lab8/shapes/orchestrator.py`) |
|   4 | Phạm Minh Tâm |      |       | — (chưa vào repo) | TV4: Evaluation, crash suite, ADR, research card, báo cáo; phần việc do `duongthuyen` làm thay |

Phân công chi tiết, file sở hữu và lịch theo checkpoint: [report/team/group_report.md](report/team/group_report.md) mục 2.

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| `duongthuyen` | Shape A `workflow` | | `src/tests/test_team_workflow.py` |
| Bùi Thu Phương (`buiphuong33`) | Shape B `single` | | `src/tests/test_team_single.py` |
| `Ngahoang2005` | Shape C `orchestrator` + handoff/trace | | `src/tests/test_team_orchestrator.py` |
| Phạm Minh Tâm (`duongthuyen` làm thay) | Evaluation + báo cáo | | `src/tests/test_team_reports.py` |

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
