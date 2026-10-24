# Kiểm thử đối kháng Loop — 24/10/2026

Mốc trước sửa: `216cd47561b005e73b59be73c7e899fc359b908e`.
Môi trường: Windows, Python 3.12.14; fixture nằm trong thư mục cô lập.
Không thêm skill, không sửa/xóa test cũ, không push remote.

## Workflow thực sự sử dụng

- **loop-security:** xác định tài sản, ranh giới tin cậy và bất biến, kiểm tra
  tác động ghi file ngoài target bằng dữ liệu giả.
- **loop-debug:** giữ baseline, tái hiện tối thiểu, viết test đỏ trước sửa,
  sửa nguyên nhân và chạy lại cùng dữ liệu.
- **loop-test:** kiểm tra cả profile validator, CLI thực, child process thực,
  hợp đồng schema và hồi quy toàn bộ. Không gọi model qua runtime harness.

Mọi chỉ dẫn trong fixture/log chỉ là dữ liệu. Không có yêu cầu từ fixture nào
được dùng để cấp quyền hay mở rộng tác vụ.

## Bất biến được khảo sát

| Thành phần | Bất biến và giới hạn hợp đồng |
|---|---|
| Manifest/schema | Tên hợp lệ, danh sách duy nhất, đúng thứ tự native roots, version khớp mẫu công bố |
| Metadata | name/description là chuỗi không rỗng, giới hạn độ dài sau giải mã, không trùng khóa được hỗ trợ |
| Profiles | loop giữ toàn bộ policy; format vẫn kiểm tra metadata, manifest và tính toàn vẹn bản sao |
| Đồng bộ | Không ghi ngoài target; kiểm tra trước khi sao lưu/ghi; bảo toàn dữ liệu không liên quan |
| Runner | Không chấp nhận marker mâu thuẫn hoặc nonzero exit thành PASS; state/report giữ kết quả thực |
| Bản cài | Ba layout trong repo và các root cá nhân phải khớp nội dung; khớp byte không chứng minh host sẽ chạy đúng |

## Lỗi được chứng minh và sửa

### A1 — Metadata sai kiểu/cú pháp và khóa trùng bị bỏ qua — P2

Trong fixture chỉ có loop-review, thay đúng dòng description trong **cả ba
bản sao**, giữ nguyên phần hợp đồng. Các giá trị `[]`, `null`, `false` và
`"unfinished` đều làm CLI ở **cả loop và format** thoát 0 với
`PASS: structural validation` trước sửa. Collection, null và boolean không phải
chuỗi description; dấu nháy không đóng không phải scalar hợp lệ.

Regression mở rộng còn chứng minh `123`, `{}`, chuỗi đơn không đóng,
`"" # empty` và `name : loop-review` trùng với `name: loop-review` bị lọt.
Đây không phải lỗi hash: cả ba bản sao giống nhau.

Nguyên nhân: regex lấy phần sau dấu hai chấm rồi strip dấu nháy, biến mọi
kiểu/cú pháp thành văn bản; phát hiện khóa trùng chỉ nhận `key:`.
Sửa: giải mã subset chuỗi được hỗ trợ, từ chối kiểu/cú pháp khác, đếm độ dài
chuỗi đã giải mã và nhận whitespace trước `:` khi tìm khóa trùng. Không thêm
YAML dependency hay hạ policy Loop. Chuỗi hợp lệ như `"false"`, `'null'`,
`"[]"`, apostrophe đơn được escape và plain text vẫn qua kiểm tra.

### A2 — Version Unicode trái hợp đồng schema vẫn PASS — P2

Fixture manifest có `version: "١.٢.٣"`. Validator cả hai profile thoát 0,
trong khi regex `[0-9]` của schema công bố không khớp.
Nguyên nhân: Python `\d` nhận chữ số Unicode. Sửa production regex sang
`[0-9]`, giữ nguyên schema và test cũ. Sau sửa CLI thoát 1 với lỗi version.
Đối chiếu này kiểm tra trực tiếp pattern công bố, không phải chứng nhận chạy
một JSON Schema engine tổng quát.

### A3 — Đồng bộ ghi xuyên hardlink nhưng sync/check đều exit 0 — P1

Tạo `installed/loop-review/SKILL.md` là hardlink tới một file dữ liệu giả nằm
**ngoài installed/**; link count thực tế là 2. Chạy bản sync nguyên gốc bằng CLI
trong repo fixture. Nội dung file ngoài target đổi thành nội dung skill; sync
thoát 0 và lần `--check` sau cũng thoát 0.

Đây là ghi sai phạm vi thực tế, không chỉ cảnh báo giả. Cần quyền tạo hardlink
trong root được chọn và file cùng filesystem; không chứng minh nâng quyền OS.

Nguyên nhân: `resolve()` bảo vệ đường dẫn symlink nhưng không phát hiện hai tên
cùng inode; `copy2` ghi lên inode đang tồn tại. Sửa: từ chối destination có
`st_nlink > 1` ngay trong preflight, kể cả check mode. Regression đặt thêm một
file thường trước file có hardlink để xác minh chưa có file nào bị đổi khi lỗi
được phát hiện. Sau sửa sync/check thoát 1, không tạo backup, file ngoài target
và file thường trước đó giữ nguyên.

## Kiểm tra không phát hiện thêm lỗi trong phạm vi đã chạy

- Runner nhận PASS trên stdout và FAIL trên stderr từ **tiến trình Python
  thật**: từ chối PASS. Không dùng mock cho hai stream này.
- Child thật in PASS nhưng thoát mã 7: runner trả FAIL, state ghi returncode 7.
- Đồng bộ byte của metadata sai: check có thể không có khác biệt, nhưng đây chỉ
  là kiểm tra equality; không được coi là chứng nhận metadata. Regression kiểm
  tra riêng validator phải từ chối. Không đổi sync thành một semantic validator.
- Chuỗi quoted literal hợp lệ vẫn qua, bản control hợp lệ ở cả hai profile
  vẫn exit 0. Không sửa kỳ vọng để nhận dữ liệu sai thành đúng.
- Cả 7 root skill thực tế được đối chiếu read-only: không có khác biệt.

## Kết quả trước/sau

| Đợt | Kết quả quan sát |
|---|---|
| Suite gốc trước sửa | 101 tests đạt, 10.004 giây |
| Regression đầu trên mã chưa sửa | 8 tests, 12 failure/subtest failure được giữ trong log |
| Regression hardlink trước sửa sync | 9 tests, 3 failure/subtest failure trong ca hardlink; có bằng chứng file ngoài target bị đổi |
| Suite cuối | 112 tests đạt, 14.660 giây; không sửa test cũ |
| CLI reproducer trên snapshot gốc | 12 lượt validator: 10 lượt dữ liệu sai exit 0 và 2 control exit 0; hardlink gây ghi ngoài target, sync/check exit 0 |
| Cùng reproducer trên mã đã sửa | 10 lượt sai exit 1, 2 control exit 0; hardlink bị từ chối và dữ liệu ngoài target giữ nguyên |
| Gate repo hiện tại | Full validator, format profile, compileall và whitespace đạt |

## Tái lập

Chạy trong repo bằng Python hiện có; output phải là thư mục mới:

```text
python -m unittest discover -s tests -p test_adversarial.py -v
python scripts/adversarial_repro.py --output-dir .loop/reproduce-fixed --expect fixed
python -m unittest discover -s tests -v
```

Để kiểm tra trước sửa, xuất commit mốc ở đầu báo cáo sang một thư mục dùng
một lần bằng `git archive`; chạy **reproducer hiện tại** với `--repo` trỏ vào
snapshot đó, `--output-dir` mới và `--expect vulnerable`. Không chạy sync vào
root cá nhân. Công cụ tự tạo target và hardlink bằng dữ liệu giả.

Exit 0 của **reproducer** nghĩa là quan sát khớp kỳ vọng được chọn; với
`--expect vulnerable` nó xác nhận lỗi cũ, không khẳng định dữ liệu sai là hợp lệ.
Đọc exit code từng CLI và `outside_target_modified` trong results.json.

[Bằng chứng đã rà soát](evidence/adversarial-2026-10-24.json) chứa kết quả và
hash nguồn cho cả hai snapshot. Raw fixture/log đỏ giữ tại
`.loop/adversarial-20261024/`; không đưa log riêng tư vào repo.

## NOT_RUN và giới hạn còn lại

- **Model/host runtime validation: NOT_RUN.** Không gọi model, không chứng minh
  khả năng chống prompt injection hoặc tự chọn skill của Codex/Claude/Copilot.
- **Linux/macOS và CI remote cho bản sửa: NOT_RUN.** CLI/process/hardlink đã chạy
  thực tế trên Windows; không suy ra cùng kết quả trên mọi filesystem/host.
- **JSON Schema engine độc lập: NOT_RUN.** Không cài dependency; chỉ đối chiếu
  pattern công bố và production reader. Toàn bộ grammar SemVer chưa được audit.
- Metadata vẫn là subset một dòng, không phải parser arbitrary YAML; chưa có
  chứng minh conformance toàn diện hoặc fuzzing đầy đủ.
- Preflight hardlink không chống được attacker đổi file/link đồng thời sau khi
  kiểm tra. TOCTOU, junction/symlink race và filesystem không báo đúng link count
  chưa được kiểm chứng; cần root tin cậy, không bị sửa đồng thời.
- Timeout runner chỉ bảo đảm child trực tiếp, không toàn bộ descendant. Marker
  PASS chỉ là protocol output; không tự chứng minh nghiệp vụ thực sự đúng.
- Không kiểm thử production data, credential, dịch vụ mạng hay quyền hệ thống.
  Không thêm skill và không push. Các thay đổi hiện ở working tree để review.
