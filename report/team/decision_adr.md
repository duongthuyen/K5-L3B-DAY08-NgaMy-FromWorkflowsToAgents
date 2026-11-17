# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: d2eafae (code 4 shape + `src/reports/benchmark.json` + `src/reports/crash.json`; commit sau chỉ sửa tài liệu)
- Run id dẫn chứng: R-workflow-C-002-s55, R-workflow-C-013-s55, R-workflow-C-014-s11 (so với R-swarm-C-002-s55 fail) trong `src/reports/benchmark.json`
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (70/70 trial, 14 claim × seed 11,22,33,44,55)
- Cost per success (mô phỏng, VND): 28.80 (single 39.44, swarm 49.57, orchestrator 57.14)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trên bộ public (không trial nào có `leak_suspect`, T07 approval hỏng và T13 approval sai claim đều pass ở cả 5 seed); số hidden do giảng viên chấm

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Benchmark `src/reports/benchmark.json` chạy cả 4 shape trên cùng 14 claim public, cùng seed `11,22,33,44,55`, cùng `pricing.yaml` và MockLLM, mỗi trial một SQLite mới. Ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000, variance 0. Swarm đạt 0.986, pass^5 0.929, variance 0.000816, fail duy nhất ở C-002 seed 55. Khi chất lượng ngang nhau thì chọn shape **ít tự chủ nhất và rẻ nhất**: workflow có cost/success 28.80 VND, thấp hơn single 27%, swarm 42%, orchestrator 50%. Workflow chỉ gọi model 1 lần mỗi trial (single 5.64, orchestrator 2.0, swarm 3.0). Mọi quyết định của workflow (số tiền, trạng thái, gọi host) là code tất định, nên không có seed nào làm kết quả đổi.

## Có đáng đổi lấy multi-agent không

Không đáng đổi trên task này. Single và orchestrator không pass cao hơn workflow trên bộ public mà tốn hơn 37–98% chi phí cho mỗi lần thành công, và có thêm chỗ cho model tác động vào luồng (chọn tool, số bước). Swarm vừa đắt hơn vừa kém hơn: ở seed 55 nó tin số ngày trễ trong ticket và hoàn tiền cho claim lẽ ra phải từ chối (R-swarm-C-002-s55). Nếu một shape multi-agent chỉ nhỉnh hơn vài điểm pass nhưng variance cao hơn, nhóm vẫn giữ workflow, vì với thao tác ghi tiền thì ổn định quan trọng hơn trung bình. Quyết định đảo lại khi task cần xử lý ngôn ngữ tự do mà luật cố định không bắt hết, ví dụ ticket không có `order_id` nhưng mô tả đủ để tìm đơn, hoặc phải tổng hợp nhiều nguồn song song. Khi đó single hay orchestrator có thể tăng pass rate trên bộ hidden đủ lớn để bù chi phí. Nhóm sẽ chỉ đổi khi benchmark trên cùng corpus và cùng seed cho thấy pass tăng vượt ngoài độ dao động giữa các seed.

## Trace và bằng chứng

Workflow ghi các event `claim` (claim_id, `found`, `has_order_id`), `lookup_order` (order view đã qua allowlist của `lookup_order`, hoặc chỉ `visible` + `reason`), `quote` (số tiền, lý do, clause_ids, parts), `issue_refund` (ok, conflict, reason), `crash` (điểm crash) và `decision` (status, proposal, reason). Cố ý **không** ghi claim row (có `parent_secret`, `raw_headers`), `principal_id`, nguyên văn ticket (có thể chứa PII hoặc câu lệnh chèn vào) và câu trả lời của model. Order row thô (SĐT, địa chỉ, tên hàng, ghi chú nội bộ) không bao giờ vào trace vì shape chỉ nhận order view đã lọc. Trace luôn được ghi trong `src/traces/<run_id>.json`, đúng chỗ scanner quét; shape không ghi log riêng hay in ra stdout. Nếu trace nằm ngoài chỗ quét được thì không chứng minh được là sạch (grader fail-closed). Vì vậy bằng chứng của nhóm là: (1) không có đường ghi nào khác ngoài `Trace.write`, (2) test `test_trace_has_no_raw_fields` quét trace và `RunResult` của cả 14 claim, (3) TV3 đã rà trace của các shape ở CP4 với 0 lần trùng.

## Giới hạn

MockLLM không phải model sản xuất; lỗi của swarm là lỗi được cài sẵn có tính tất định (`seed % 5 == 0`), nên kết quả so sánh chỉ đúng cho môi trường mô phỏng này. Latency để `unavailable`. Cost là VND mô phỏng từ `pricing.yaml`, không phải hóa đơn API. Bộ public chỉ có 14 claim và chỉ một claim có delay trong ticket khác order row, nên pass rate 1.000 trên public chưa bảo đảm đạt ngưỡng hidden. Tự kiểm trên `student_drop/` (`src/reports/hidden_selfcheck.json`, 40 claim × 5 seed, không nhãn): workflow chạy hết 200/200 trial, không lỗi, không `leak_suspect`, và cho cùng trạng thái với single và orchestrator ở cả 200 trial. Điều này cho thấy chọn workflow không làm mất gì so với hai shape kia trên bộ hidden. Tuy vậy, tự kiểm không có nhãn nên không thay được pass rate chính thức của grader. Các file JSON trong `src/reports/` do lệnh sinh ra, không sửa tay.
