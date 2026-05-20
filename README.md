# NTGroup_Healthio

# Bài tập lớn môn Các công nghệ lập trình hiện đại
## Thành viên
| MSSV | Họ tên
|------|--------
| 2351050111 | Đào Thị Kim Ngân
| 2351050165 | Bùi Thiên Hương Thảo
## Mô tả dự án
### 1. Tổng quan dự án
    Ứng dụng quản lí sức khoẻ và theo dõi hoạt động cá nhân
### 2. Các chức năng chính và ràng buộc của hệ thống 
#### Xác thực và phân quyền: 
- Đăng nhập, đăng ký với vai trò người dùng hoặc chuyên gia dinh dưỡng/huấn luyện
viên.
- Người dùng có thể chọn chế độ theo dõi cá nhân hoặc kết nối với chuyên gia để
nhận tư vấn.
#### Quản lý hồ sơ sức khỏe:
- Người dùng nhập thông tin cá nhân: chiều cao, cân nặng, tuổi, mục tiêu sức khỏe.
- Theo dõi chỉ số BMI, lượng nước uống, số bước đi, nhịp tim.
#### Lập kế hoạch tập luyện và dinh dưỡng:
- Tạo lịch tập luyện cá nhân với các bài tập gợi ý hoặc tự thêm bài tập.
#### Theo dõi và nhắc nhở:
- Đặt nhắc nhở uống nước, tập luyện, nghỉ ngơi.
- Thống kê số liệu hàng tuần/tháng bằng biểu đồ: thời gian tập luyện, lượng calo tiêu thụ.
#### Tương tác và hỗ trợ:
- Người dùng có thể viết nhật ký sức khỏe, lưu lại cảm nhận sau mỗi buổi tập.
  
## Các công nghệ sử dụng 
### Backend: 
- Django & Django REST Framework: Xây dựng các RESful API, xử lí các logic nghiệp vụ và phân quyền người dùng.
- OAuth 2.0 : Cơ chế xác thực và phân quyền người dùng, đảm bảo an toàn cho dữ liệu cá nhân.
### Database: MySQLWorkbench
- Lưu trữ toàn bộ thông tin về người dùng, dữ liệu người dùng.
### Khác
- Swagger: Trực quan hoá các API, hỗ trợ việc kết nối với Frontend.
#### Cảm ơn bạn đã đọc!


