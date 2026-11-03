# Gói việc agent-workflows — audit và thực nghiệm sạch

Owner chat: Kiểm tra repo Agent workflow.
Repo độc quyền sửa: the agent-workflows repository.
Đọc README.md và EVIDENCE-CONTRACT.md trong task trước, rồi repo AGENTS/map.

| ID | Ưu tiên | Việc cần làm | Tiêu chí hoàn tất |
|---|---|---|---|
| WF-01 | P0 | Reproduce saved Copilot workflow/revision và combined subset; audit oracle/aggregator | Số liệu raw/functional khớp, original labels immutable, sorted order explicit |
| WF-02 | P0 | Sửa/viết harness trong repo bằng code maintainable, không phụ thuộc script local Copilot | Stop/resume bền vững, functional/policy/file-integrity phân lớp, negative controls PASS |
| WF-03 | P0 | Thiết kế comparator ngang thông tin và history | No-skill không cue/skill; full prompt không đáp án oracle; follow-up nhận actual history hoặc nhãn restarted |
| WF-04 | P1 | Pilot 2 ca × 3 nhóm × 2 repeats =12 CLI tối đa | Freeze protocol; cân thứ tự; no-skill/workflow/info-matched prompt; độc lập checker; đủ usage/pins hoặc BLOCKED thật |
| WF-05 | P1 | Xem lại workflow task routing/graph-map chỉ khi test chứng minh lỗi | Smallest fix, regression before/after; không nhồi instruction để thắng benchmark |
| WF-06 | P1 | Gói evidence + biểu đồ + docs publish | Dữ liệu/script/figures đi cùng diff; gates/CI đúng SHA; báo cáo âm nếu không tốt hơn |

## Phạm vi thực nghiệm

Chọn revision đã làm rõ ID sort và một ca nhiều nguồn/requirements revision hoặc
policy-conflict đủ để workflow có cơ hội dùng cơ chế của mình. Không chỉ lặp cents.
Giữ bài toán tự nhiên, oracle ẩn không lộ đáp án, có một source-injection/approval
boundary. No-skill, loop-work/workflow được chọn đúng nhiệm vụ, và information-matched
single prompt. 2 repeat/case/arm chỉ là pilot, không kết luận statistical superiority.
Setup cost/map design nếu dùng phải báo riêng; đo direct execution và graph/map
không đánh đồng. Combined/selective routing giai đoạn sau chỉ lập protocol/nhận xét
lịch sử; không phát sinh thêm CLI ngoài12. Không đọc bản đang bị attention chat sửa:
nếu cần skill attention cho phân tích thì dùng frozen snapshot đã pin, chỉ đọc.

## Figures tối thiểu

1. Acceptance theo case/arm, phân biệt original/functional và n.
2. Token và elapsed theo từng repeat, có chỉ báo CLI count và cache.
3. Cost-quality scatter hoặc paired deltas, bảng số tương ứng.
4. Historical-vs-new labels và STOP/BLOCKED/NOT_RUN coverage nếu pilot không đủ.

## Thứ tự và đường dẫn đầu ra

P0 measurement repair/tests -> protocol freeze -> bounded pilot -> analysis/figures
-> full gates/publication -> push evidence cùng code. Cập nhật TASK-STATUS.md sau
mỗi batch. Dùng task/evidence/<run-id>/ cho dữ liệu public nhỏ, hoặc vị trí evidence
chuẩn hiện có trong repo và link rõ từ task. Log thô dưới .loop, không public.
Task không bắt tạo new release/version nếu chỉ report; product patch theo contract.
Đừng sửa parent AGENTS/MAP hay repo attention trong khi hai chat chạy song song.
