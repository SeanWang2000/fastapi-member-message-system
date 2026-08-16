# FastAPI 會員留言系統

FastAPI 學習後的實作練習，用於整合會員註冊、登入驗證、Session 管理與留言功能。

目前已完成主要功能實作，系統可正常操作，後續將持續整理程式碼與專案結構，並視情況增加新功能。

## 系統畫面

### 登入頁面

![登入頁面](images/login.png)

### 註冊頁面

![註冊頁面](images/register.png)

### 留言板頁面

![留言板頁面](images/message-board.png)
## 使用方式

在第一個終端機啟動後端 API：

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

在第二個終端機啟動前端靜態伺服器：

```powershell
cd frontend
python -m http.server 5173
```

接著在瀏覽器開啟：

```text
http://127.0.0.1:5173
```

## 使用 Docker Compose

啟動 backend 與 frontend：

```powershell
docker compose up --build
```

啟動後：

- Frontend：http://localhost:5173
- Backend API：http://localhost:8000

停止服務：

```powershell
docker compose down
```
